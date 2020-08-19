# -*- coding: utf-8 -*-
import os
import app.utils as appUtils
from settings import Config
from .models import Data
from app.app import celery
from app.mc import mc

TC_MAX_NUM = 6
extract_vcf_sample_script = os.path.join(Config.SCRIPT_PATH,
                                         Config.EXTRACT_VCF_SAMPLE)
split_vcf_sample_script = os.path.join(Config.SCRIPT_PATH,
                                       Config.SPLIT_VCF_SAMPLE)


def tc_map(vcf, vcf_type, samples):
    tc_series = []
    last_id = len(Data.query.all())
    _trans = {"WES": "E", "WGS": "G", "RNAseq": "R"}
    f = open(os.path.join(Config.VCF_FILE_PATH, vcf + '.idmap'), 'w')
    for i in range(len(samples)):
        tmp = last_id + 1 + i
        tc_id = "TC" + _trans[vcf_type] + "0" * (TC_MAX_NUM -
                                                 len(str(tmp))) + str(tmp)
        tc_series.append([tc_id, samples[i]])
        f.write("\t".join([tc_id, samples[i]]) + "\n")
    f.close()
    return tc_series


def fetch_vcf_samples(vcf, vcf_type="WES"):
    # split vcf return each sample
    fetch_sample_cmd = "sh {script} {vcf}".format(
        script=extract_vcf_sample_script, vcf=vcf)
    appUtils.processor.shRun(fetch_sample_cmd)
    f = open(os.path.join(Config.VCF_FILE_PATH, vcf + '.sample_name'), 'r')
    samples = [each.strip() for each in f.readlines()]
    f.close()
    tc_series = tc_map(vcf, vcf_type, samples)
    # split each sample
    split_vcf_cmd = "sh {script} {vcf} {map_file}".format(
        script=split_vcf_sample_script, vcf=vcf, map_file=vcf + '.idmap')
    appUtils.processor.shRun(split_vcf_cmd)
    return tc_series


@celery.task
def async_fetch_vcf_samples(vcf, username, upload_id, vcf_type="WES"):
    # split vcf return each sample
    fetch_sample_cmd = "sh {script} {vcf}".format(
        script=extract_vcf_sample_script, vcf=vcf)
    appUtils.processor.shRun(fetch_sample_cmd)
    f = open(os.path.join(Config.VCF_FILE_PATH, vcf + '.sample_name'), 'r')
    samples = [each.strip() for each in f.readlines()]
    f.close()
    tc_series = tc_map(vcf, vcf_type, samples)
    # split each sample
    split_vcf_cmd = "sh {script} {vcf} {map_file}".format(
        script=split_vcf_sample_script, vcf=vcf, map_file=vcf + '.idmap')
    appUtils.processor.shRun(split_vcf_cmd)
    mc.delete('wheatgmap.{0}.data'.format(username))  # 删除在redis的旧缓存
    # creare sample in mysql
    for each in tc_series:
        row = Data(tc_id=each[0],
                   provider=username,
                   sample_name=each[1],
                   type=vcf_type,
                   upload_id=upload_id)
        row.save()
    appUtils.finish_task(upload_id)
    appUtils.logger().info('cache delete: wheatgmap.{0}.data'.format(username))
    return {
        'task': 'vcf_upload',
        'result': '{0} upload success...'.format(vcf),
    }