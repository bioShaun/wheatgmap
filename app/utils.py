# -*- coding: utf-8 -*-
# 集成 celery
import re
import math
import redis
import vcfpy
import random
import logging
import requests
import subprocess
import pandas as pd
from app.db import DB
from app.mc import cached
from settings import Config
from flask_login import current_user
from app.auth.models import Data, TaskInfo

CACHE_PREFIX = Config.CACHE_PREFIX


def logger(log_file=''):
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


#@cached('wheatgmap.{name}.data', expire=3600)
def fetch_vcf(name):
    pub_vcf = Data.query.filter_by(opened=1, sign=0).all()
    pub_samples = [
        '.'.join([each.tc_id, each.sample_name]) for each in pub_vcf
    ]
    if name != 'anonymous':
        own_vcf = Data.query.filter_by(provider=name, opened=0, sign=0).all()
        private_samples = [
            '.'.join([each.tc_id, each.sample_name]) for each in own_vcf
        ]
    else:
        private_samples = []

    return pub_samples, private_samples


@cached('wheatgmap.sample.{table}', expire=3600)
def fetch_sample(table, fixed_column_num):
    cmd = "select COLUMN_NAME from information_schema.COLUMNS where table_name='{table}';".format(
        table=table)
    db = DB()
    results = db.execute(cmd)
    results = [each[0] for each in results]
    return results[fixed_column_num:]


def randSeq(k=10):
    origin_seq = "aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ1234567890"
    return ''.join(random.sample(list(origin_seq), k))


def parseResult(filepath, header=True, sep='\t'):
    body = []
    try:
        f = open(filepath, 'r')
        if header:
            head = f.readline().strip().split(sep)
        else:
            head = []
        row = f.readline()
        while row:
            row_list = row.strip().split(sep)
            body.append(row_list)
            row = f.readline()
        return {'header': head, 'body': body}
    except:
        return {'header': [], 'body': []}


class processor(object):
    '''
    use subprocess Popen & communicate
    '''
    @classmethod
    def Run(cls, cmd):
        subprocess.call(cmd, shell=True)
        return None

    @classmethod
    def shRun(cls, cmd, sudo=False):
        if sudo:
            cmd = ' '.join(['sudo', cmd])

        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        #print(stderr)
        #print(stdout)
        if stdout:
            return str(stdout, encoding='utf-8').strip().split('\n')
        elif stderr:
            print(str(stderr, encoding='utf-8'))
            return []
        else:
            return []


def parseInput(listStr, max_input=100):
    if ',' in listStr:
        gene_list = []
        genes = [each.split(',') for each in listStr.split()]
        for gene_part in genes:
            gene_list += gene_part
    else:
        gene_list = listStr.split()
    if len(gene_list) > max_input:
        return []
    return gene_list


def printPretty(String, max_row_len=25, sep='\n'):
    if len(String) > max_row_len:
        i = 0
        over_len = math.ceil(len(String) / max_row_len) * max_row_len
        tmp_str = ""
        while i < over_len:
            tmp_str += String[i:i + max_row_len] + sep
            i += max_row_len
        return tmp_str
    return String


def geneOuterLink(gene: str):
    link_address = {
        'at':
        'https://www.arabidopsis.org/servlets/TairObject?type=locus&name='
    }
    gene_pre = gene[:2].lower()
    gene_link = link_address.get(gene_pre)
    if gene_link:
        return f'<a href="{gene_link}{gene}">{gene}</a>'
    else:
        return gene


def addOuterLink(orth_genes):
    orth_gene_list = orth_genes.split(',')
    orth_link_list = [geneOuterLink(gene) for gene in orth_gene_list]
    return ', '.join(orth_link_list)


class redisTask(object):
    def __init__(self, task_len=5):
        self._task_length = task_len
        self._rdp = redis.ConnectionPool(host='localhost',
                                         password='wheatdb',
                                         port=6379,
                                         decode_responses=True)
        self.conn = redis.StrictRedis(connection_pool=self._rdp)
        self.flower_url = 'http://127.0.0.1:5555'
        self.redis_celery_pattern = r'celery-task-meta-*'

    def fetch_task(self, username):
        backtasks = []
        all_celery_tasks = [
            re.sub(self.redis_celery_pattern, '', key)
            for key in self.conn.keys()
            if re.match(self.redis_celery_pattern, key)
        ]
        try:
            user_tasks = self.conn.lrange(username, 0, -1)  # get all task uuid
            tasks = list(set(all_celery_tasks) & set(user_tasks))
        except:
            tasks = []
        tasks = tasks if len(
            tasks) <= self._task_length else tasks[:self._task_length]
        if tasks:
            for task in tasks:
                tmp = {}
                url = '{root_url}/api/task/result/{id}'.format(
                    root_url=self.flower_url, id=task)
                reply = requests.get(url).json()
                tmp['id'] = task
                tmp['state'] = reply['state']
                backtasks.append(tmp)
        return backtasks

    def push_task(self, username, task_id):
        return self.conn.rpush(username, task_id)


redis_task = redisTask()


def vcfValidator(vcf):
    try:
        reader = vcfpy.Reader.from_path(vcf)
    except FileNotFoundError as e:
        return 'Upload Failed.'
    except vcfpy.VCFPyException as e:
        return f'VCF format Error: [{e}]'
    except Exception as e:
        return str(e)
    else:
        if 'AD' not in reader.header._indices['FORMAT']:
            print("ad wrong")
            return 'Allelic depths information is missing from vcf.'

        chr_size_df = pd.read_csv(Config.COMPLETE_CHROM_SIZE,
                                  sep='\t',
                                  header=None,
                                  names=['chrom_len'],
                                  index_col=0)
        contig_info = reader.header.get_lines(key='contig')
        if contig_info:
            for chr_i in contig_info:
                if chr_i.id not in chr_size_df.index:
                    return f'Invalid chromosome [{chr_i.id}].'
                else:
                    iwgsc_chr_len = chr_size_df.loc[chr_i.id].chrom_len
                    if int(chr_i.length) != iwgsc_chr_len:
                        error_msg = (
                            f'Wrong chromosome length for {chr_i.id}'
                            f'[vcf: {chr_i.length}; IWGSC(v1.0): {iwgsc_chr_len}].'
                        )
                        return error_msg
        else:
            return 'Chromosome information is missing from vcf file.'
    return False


def fetch_vcf_by_task(upload_id):
    upload_id_list = [each.strip() for each in upload_id.split(',')]
    task_vcf = Data.query.filter(Data.upload_id.in_(upload_id_list)).all()
    return ['.'.join([each.tc_id, each.sample_name]) for each in task_vcf]


def tasks_status(task_ids):
    task_list = task_ids.split(',')
    task_info_list = [(task_id, TaskInfo.findByTaskId(task_id))
                      for task_id in task_list]
    running_tasks = []
    failed_tasks = []
    invalid_tasks = []
    for task_i_id, task_i_info in task_info_list:
        if task_i_info is None:
            invalid_tasks.append(task_i_id)
        else:
            if task_i_info.task_status == 'running':
                running_tasks.append(task_i_id)
            elif task_i_info.task_status == 'finished':
                pass
            else:
                failed_tasks.append(task_i_id)

    def task_out_str(tasks_list, prefix):
        if tasks_list:
            out_str = ','.join(tasks_list)
            return f'{prefix} Tasks: {out_str}'

    status_str_list = [
        task_out_str(each[0], each[1])
        for each in [(invalid_tasks,
                      'Invalid'), (failed_tasks,
                                   'Failed'), (running_tasks, 'Running')]
        if task_out_str(each[0], each[1])
    ]

    if status_str_list:
        return ';'.join(status_str_list)
    else:
        return 'all_done'


def finish_task(task_id):
    task_info = TaskInfo.findByTaskId(task_id)
    task_info.task_status = 'finished'
    task_info.save()