import os
from app.db import DB
import pandas as pd
import numpy as np
import copy
import time
import math
import subprocess
from sklearn.decomposition import PCA
from settings import basedir
from app.utils import processor, printPretty
from app.app import celery
from settings import Config

UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'download')
vcf_seq_script = os.path.join(Config.SCRIPT_PATH, Config.VCF_SEQ)
vcf_ann_script = os.path.join(Config.SCRIPT_PATH, Config.VCF_ANN)
vcf_pca_script = os.path.join(Config.SCRIPT_PATH, Config.VCF_PCA)


def wildcard_gene(genename):
    return '%'.join([genename[:10], genename[11:]])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ('xlsx', 'csv', 'txt')


def query_gene_by_pos(chrom, start, end, **kargs):
    if chrom and start and end:
        gene_bed_df = pd.read_csv(Config.GENE_POS,
                                  sep='\t',
                                  header=None,
                                  names=['chrom', 'start', 'end', 'gene'])
        filter1 = gene_bed_df.chrom == chrom
        filter2 = gene_bed_df.start >= int(start)
        filter3 = gene_bed_df.end <= int(end)
        region_gene_df = gene_bed_df[filter1 & filter2 & filter3]
        return list(region_gene_df.gene)
    return []


def batch_query_gene(gene_list, max_input=1000):
    '''
    get a gene string by search locus database
    '''

    if len(gene_list) > max_input:
        return []
    if len(gene_list) == 1:
        _search = "('{0}')".format(gene_list[0])
    else:
        _search = tuple([str(each) for each in gene_list])
    db = DB()
    cmd = """select l.*, f.Description, f.Pfam_Description,
                     f.Interpro_Description, f.GO_Description from locus l left join func f
                     on l.GENE_ID=f.GENE_ID where l.GENE_ID in {0};
          """.format(_search)
    result = db.execute(cmd)
    if result:
        result = [(each[1], ) + each[5:] for each in result]
        df1 = pd.DataFrame(result)
        df2 = pd.DataFrame(gene_list)
        df3 = pd.merge(df2, df1, how='left').fillna("")
        return [list(df3.iloc[i, :]) for i in range(len(df3))]
    return []


def fetch_blast_result(genename):
    MAX_ROW_LEN = 125
    db = DB()
    command = "select GENE_ID,VAL from {table} where GENE_ID like '{gene}%'"
    pep_results = db.execute(
        command.format(table='pep_tb', gene=wildcard_gene(genename)))
    cds_results = db.execute(
        command.format(table='cds_tb', gene=wildcard_gene(genename)))
    if len(pep_results) == 0 and len(cds_results) == 0:
        return {}
    pro_seq = {k: v for k, v in pep_results}
    cds_seq = {k: v for k, v in cds_results}
    # print it pretty
    for k, v in pro_seq.items():
        if len(v) > MAX_ROW_LEN:
            i = 0
            over_len = math.ceil(len(v) / MAX_ROW_LEN) * MAX_ROW_LEN
            tmp_str = ""
            while i < over_len:
                tmp_str += v[i:i + MAX_ROW_LEN] + '\n'
                i += MAX_ROW_LEN
            pro_seq[k] = tmp_str

    for k, v in cds_seq.items():
        if len(v) > MAX_ROW_LEN:
            i = 0
            over_len = math.ceil(len(v) / MAX_ROW_LEN) * MAX_ROW_LEN
            tmp_str = ""
            while i < over_len:
                tmp_str += v[i:i + MAX_ROW_LEN] + '\n'
                i += MAX_ROW_LEN
            cds_seq[k] = tmp_str

    return {'pro_seq': pro_seq, 'cds_seq': cds_seq}


def get_locus_result(genename, blast_results):
    cds_seq_dict = blast_results.get('cds_seq', 'NA')
    pro_seq_dict = blast_results.get('pro_seq', 'NA')
    db = DB()
    locus_result = {}
    cmd = """select l.*, f.Description, f.Pfam_Description,
             f.Interpro_Description, f.GO_Description from locus l left join func f
             on l.GENE_ID=f.GENE_ID where l.GENE_ID='{0}';
          """.format(genename)
    result = db.execute(cmd, get_all=False)
    if result:
        locus_result['orthologous_gene'] = {}
        ortho_header = [
            'Arabidopsis_thaliana', 'Hordeum_vulgare', 'Oryza_sativa',
            'Triticum_aestivum', 'Zea_mays'
        ]
        locus_result['orthologous_gene']['header'] = ortho_header
        locus_result['orthologous_gene']['body'] = []
        cmd = "select l.GENE_ID, o.* from locus l left join ortho o on l.GENE_ID=o.GENE_ID where l.GENE_ID='{0}';".format(
            genename)
        ortho_result = db.execute(cmd, get_all=False)
        if ortho_result:
            ortho_result_list = ortho_result[3:]
            ortho_result_list = [
                printPretty(each) for each in ortho_result_list
                if each is not None
            ]
            locus_result['orthologous_gene']['body'] = ortho_result_list
        gene_id, chr, pos_start, pos_end = result[1:5]
        description, pfam_desc, interpro_desc, go_desc = result[5:]
        locus_result['gene_identification'] = {
            'Gene Product Name': description,
            'Locus Name': genename
        }
        locus_result['gene_attributes'] = {
            'Chromosome': chr,
            "Gene Postion": '{start} - {end}'.format(start=pos_start,
                                                     end=pos_end)
        }
        header = [
            'Description', 'Pfam_Description', 'Interpro_Description',
            'GO_Description'
        ]
        locus_result['gene_annotation'] = {}
        locus_result['gene_annotation']['header'] = header
        locus_result['gene_annotation']['body'] = [
            description, pfam_desc, interpro_desc, go_desc
        ]
        # match 01G and 02G TraesCS1A02G000100
        #result = db.execute("select * from tissue_expression where Gene_id='{0}'".format(genename))
        result = db.execute(
            "select * from tissue_expression where Gene_id like '{0}'".format(
                wildcard_gene(genename)))
        if result:
            row = [float(each) for each in result[0][2:]]
        else:
            row = []
        locus_result['tissue_expression'] = row
        locus_result['gene_cds_seq'] = cds_seq_dict
        locus_result['gene_pro_seq'] = pro_seq_dict
    return locus_result


def fetch_sequence(table, chr, start_pos, end_pos):
    cmd = "python {script} \
    --refer /home/data/wheat/reference/Chinese_Spring_v1.0.fasta \
    --in_vcf {data_path}/{table}.vcf.gz \
    --sample_name {sample}  \
    --chrom {chr} \
    --start_pos {start_pos} \
    --end_pos {end_pos}".format(script=vcf_seq_script,
                                data_path=Config.VCF_SAMPLE_PATH,
                                table=table,
                                sample=table.split(".")[1],
                                chr=chr,
                                start_pos=start_pos,
                                end_pos=end_pos)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p.wait()
    result = p.stdout.readlines()
    result = ''.join([
        str(each, encoding="utf-8").replace('\n', '<br/>') for each in result
    ])
    return result


def _pandas_read(filename, header):
    suffix = filename.rsplit('.', 1)[1].lower()
    if suffix == 'csv':
        df = pd.read_csv(filename, header=header)
    elif suffix == 'xlsx':
        df = pd.read_excel(filename, header=header)
    elif suffix == 'txt':
        df = pd.read_table(filename, header=header)
    return df


def run_pca(filename, sample_group):
    pca = PCA(n_components=2)
    df = _pandas_read(os.path.join(UPLOAD_FOLDER, 'pca', filename), header=0)
    mat = [
        list(each)
        for each in pca.fit_transform(np.log2(df.iloc[:, 1:] + 1).T)
    ]

    if sample_group:
        sample_df = _pandas_read(os.path.join(UPLOAD_FOLDER, 'group',
                                              sample_group),
                                 header=None)
        group = list(sample_df.iloc[:, 0])
        sample = list(sample_df.iloc[:, 1])

    else:
        group = list(df.columns[1:])
        sample = copy.copy(group)

    for i in range(len(mat)):
        mat[i].append(group[i])
        mat[i].append(sample[i])

    return mat


def run_vcf(filepath):
    tmp_pca_path = os.path.join(UPLOAD_FOLDER, 'pca', 'tmp.pca.txt')
    command = "sh {0} {1} {2}".format(vcf_pca_script, filepath, tmp_pca_path)
    p = subprocess.Popen(command, shell=True)
    p.wait()

    df = pd.read_table(tmp_pca_path)
    # subprocess.call("rm -rf {0} {1}".format(filepath, tmp_pca_path), shell=True)
    mat = []
    for i in range(len(df)):
        mat.append(list(df.iloc[i, 1:]))

    group = list(df['ID'])
    sample = copy.copy(group)

    for i in range(len(mat)):
        mat[i].append(group[i])
        mat[i].append(sample[i])

    return mat


def run_annotation(vcf_file, annotation_database):
    annotation_prefix = '-'.join(
        [str(int(time.time())),
         vcf_file.split('.vcf.gz')[0]])
    cmd = "{script}  {vcf_file} {annotation_database} {prefix}".format(
        script=vcf_ann_script,
        vcf_file=os.path.join(UPLOAD_FOLDER, 'vcf_ann', vcf_file),
        annotation_database=annotation_database,
        prefix=os.path.join(UPLOAD_FOLDER, 'vcf_ann', annotation_prefix))
    processor.shRun(cmd)
    processor.Run("zip {zipfile} {files}".format(
        zipfile=os.path.join(UPLOAD_FOLDER, 'vcf_ann',
                             annotation_prefix + '.zip'),
        files=os.path.join(UPLOAD_FOLDER, 'vcf_ann', annotation_prefix) +
        '.ann.vcf.*'))
    return annotation_prefix + '.zip'


@celery.task
def async_run_annotation(vcf_file, annotation_database):
    annotation_prefix = '-'.join(
        [str(int(time.time())),
         vcf_file.split('.vcf.gz')[0]])
    cmd = "{script}  {vcf_file} {annotation_database} {prefix}".format(
        script=vcf_ann_script,
        vcf_file=os.path.join(UPLOAD_FOLDER, 'vcf_ann', vcf_file),
        annotation_database=annotation_database,
        prefix=os.path.join(UPLOAD_FOLDER, 'vcf_ann', annotation_prefix))
    processor.shRun(cmd)
    processor.Run("zip {zipfile} {files}".format(
        zipfile=os.path.join(UPLOAD_FOLDER, 'vcf_ann',
                             annotation_prefix + '.zip'),
        files=os.path.join(UPLOAD_FOLDER, 'vcf_ann', annotation_prefix) +
        '.ann.vcf.*'))
    result = annotation_prefix + '.zip'
    return {'task': 'vcf_ann', 'result': result}
