# -*- coding: utf-8 -*-
# 集成 celery
import re
import math
import redis
import vcfpy
import random
import requests
import subprocess
import pandas as pd
from app.db import DB
from settings import Config


def fetch_sample(table, fixed_column_num):
    cmd = "select COLUMN_NAME from information_schema.COLUMNS where table_name='{table}';".format(table=table)
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
            tmp_str += String[i:i+max_row_len] + sep
            i += max_row_len
        return tmp_str
    return String


class redisTask(object):
    def __init__(self, task_len=5):
        self._task_length = task_len
        self._rdp = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.conn = redis.StrictRedis(connection_pool=self._rdp)
        self.flower_url = 'http://127.0.0.1:5555'
        self.redis_celery_pattern = r'celery-task-meta-*'

    def fetch_task(self, username):
        backtasks = []
        all_celery_tasks = [re.sub(self.redis_celery_pattern, '', key) for key in self.conn.keys() if re.match(self.redis_celery_pattern, key)]
        try:
            user_tasks = self.conn.lrange(username, 0, -1) # get all task uuid
            tasks = list(set(all_celery_tasks) & set(user_tasks))
        except:
            tasks = []
        tasks = tasks if len(tasks) <= self._task_length else tasks[:self._task_length]
        if tasks:
            for task in tasks:
                tmp = {}
                url = '{root_url}/api/task/result/{id}'.format(root_url=self.flower_url, id=task)
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
    except Exception as e:
        return str(e)
    else:
        if 'AD' not in reader.header._indices['FORMAT']:
            print("ad wrong")
            return 'Allelic depths information is missing from vcf.'

        chr_size_df = pd.read_csv(Config.CHROM_SIZE,
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


        




