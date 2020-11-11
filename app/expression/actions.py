# -*- coding: utf-8 -*-
import os
import time
import subprocess
from settings import basedir
from app.utils import processor, randSeq
from app.app import celery
from app.db import DB
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import copy

UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'download')
KOBAS_PATH = '/home/zxchen/miniconda3/envs/kobas/bin/python'
ENRICH_SCRIPT = '/home/scripts/omWheatGeneEnrich/genelist_enrich.py'

def run_enrich(specie, genes):
    tmp_dir = randSeq(k=5)
    enrich_dir = os.path.join(UPLOAD_FOLDER, 'enrich', tmp_dir)
    processor.Run("mkdir {tmpDir}".format(tmpDir=enrich_dir))
    filepath = os.path.join(enrich_dir, 'tmp.gene.list')
    f = open(filepath, 'w')
    for each in genes:
        f.write(each + '\n')
    f.close()
    cmd = "{pypath} {script} \
     -s '{specie}' \
     -g {genelist} \
     -o {dir}".format(pypath=KOBAS_PATH, script=ENRICH_SCRIPT, specie=specie, genelist=filepath, dir=enrich_dir)
    result = processor.shRun(cmd)
    href = []
    body = []
    try:
        f = open(os.path.join(enrich_dir, 'enrich.txt'), 'r')
        head = f.readline().strip().split('\t')
        head = head[:7] + head[9:]
        row = f.readline()
        while row:
            row_list = row.strip().split('\t')
            href.append(row_list[8])
            body.append(row_list[:7] + row_list[9:])
            row = f.readline()
        # processor.Run("rm -rf {0}".format(enrich_dir)) 
        return {'header': head, 'body': body, 'href': href}
    except IOError as e:
        print(e)
        # processor.Run("rm -rf {0}".format(enrich_dir))
        return {'header': [], 'body': [], 'href': []}
  
    return result


@celery.task
def async_run_enrich(specie, genefile):
    tmp_dir = randSeq(k=5)
    enrich_dir = os.path.join(UPLOAD_FOLDER, 'enrich', tmp_dir)
    processor.Run("mkdir {tmpDir}".format(tmpDir=enrich_dir))
    if type(genefile) == type([]):
        filepath = os.path.join(enrich_dir, 'tmp.gene.list')
        f = open(filepath, 'w')
        for each in genefile:
            f.write(each + '\n')
        f.close()
    else:
        filepath = os.path.join(enrich_dir, genefile)
        processor.Run("mv {gene_file} {tmpDir}".format(
                gene_file=os.path.join(UPLOAD_FOLDER, 'enrich', genefile),
                tmpDir=enrich_dir))
    cmd = "{pypath} {script}\
     -s '{specie}' \
     -g {genelist} \
     -o {dir}".format(pypath=KOBAS_PATH, script=ENRICH_SCRIPT, specie=specie, genelist=filepath, dir=enrich_dir)
    # print(cmd)
    # print(os.environ['HOME'])
    processor.shRun(cmd)
    href = []
    body = []
    try:
        f = open(os.path.join(enrich_dir, 'enrich.txt'), 'r')
        head = f.readline().strip().split('\t')
        head = head[:7] + head[9:]
        row = f.readline()
        while row:
            row_list = row.strip().split('\t')
            href.append(row_list[8])
            body.append(row_list[:7] + row_list[9:])
            row = f.readline()
        # processor.Run("rm -rf {0}".format(enrich_dir)) 
        return {'task': 'enrich', 'result': {'header': head, 'body': body, 'href': href}}
    except IOError as e:
        print(e)
        # processor.Run("rm -rf {0}".format(enrich_dir))
        return {'task': 'enrich', 'result': {'header': [], 'body': [], 'href': []}}


def fetch_expression_data(gene_id, samples, table="rename_iwgsc_refseq"):
    sample_str = ','.join(samples)
    cmd = "select {samples} from {table} where gene='{gene}'".format(
        samples=sample_str,
        table=table,
        gene=gene_id)
    db = DB()
    results = db.execute(cmd)
    if len(results) == 0:
        return []
    return list(results[0])


def fetch_expression_plot_data(samples, table="iwgsc_refseq"):
    pca = PCA(n_components=2)
    sample_str = ','.join(['gene'] + samples)
    cmd = "select {samples} from {table}".format(
        samples=sample_str,
        table=table
    )
    engine = create_engine('mysql+pymysql://wheatdb:wheatdb@localhost:3306/VCFDB')
    df = pd.read_sql_query(cmd, engine)
    mat = [list(each) for each in pca.fit_transform(np.log2(df.iloc[:,1:].astype('float')+1).T)]
    group = list(df.columns[1:])
    sample = copy.copy(group)
    
    for i in range(len(mat)):
        mat[i].append(group[i])
        mat[i].append(sample[i])
    return mat
