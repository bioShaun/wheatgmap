import enum
import os
import re
from typing import List

from sqlalchemy.orm import query
from app.db import DB
import pandas as pd
import numpy as np
import copy
import time
import math
import subprocess
from sklearn.decomposition import PCA
from settings import basedir
from app.utils import processor, addOuterLink
from app.app import celery
from settings import Config
from app.auth.models import GeneExpression, LncExpression, RnaNeighbor, GeneSeq
from scipy import stats
from itertools import product
from scipy.cluster.hierarchy import complete, leaves_list
from scipy.spatial.distance import pdist
from itertools import groupby
from operator import itemgetter

UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'download')
vcf_seq_script = os.path.join(Config.SCRIPT_PATH, Config.VCF_SEQ)
vcf_ann_script = os.path.join(Config.SCRIPT_PATH, Config.VCF_ANN)
vcf_pca_script = os.path.join(Config.SCRIPT_PATH, Config.VCF_PCA)

VAR_DENSITY_PATH = os.path.join(UPLOAD_FOLDER, 'var_density')

GENE_PATTERN = re.compile('TraesCS(\w+)1G(\w+)')


def transfer_id(gene_id):
    """
    TraesCS3D01G355600 -> TraesCS3D02G355600
    """
    if GENE_PATTERN.match(gene_id):
        id_1, id_2 = GENE_PATTERN.match(gene_id).groups()
        return 'TraesCS{id_1}2G{id_2}'.format(**locals())
    else:
        return gene_id


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


def fetch_gene_seq(geneId, feature):
    seq_res = GeneSeq.query.filter_by(gene_id=geneId, feature=feature).all()
    seq_list = [item.as_dict() for item in seq_res]
    tr_seq_dict = {}
    for tr_id, seq_data in groupby(seq_list, key=itemgetter("transcript_id")):
        tr_seq = [each['seq'] for each in seq_data]
        tr_seq_dict[tr_id] = '\n'.join(tr_seq)
    return tr_seq_dict


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
                addOuterLink(each) for each in ortho_result_list
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
            row = [np.log2(float(each) + 1) for each in result[0][2:]]
        else:
            row = []
        locus_result['tissue_expression'] = row
        locus_result['gene_cds_seq'] = cds_seq_dict
        locus_result['gene_pro_seq'] = pro_seq_dict

        geneExp = GeneExpression.findbygene(transfer_id(genename))
        locus_result['dev_expression_stage'] = [
            each.tissue for each in geneExp
        ]
        locus_result['dev_expression_tpm'] = [
            np.log2(each.tpm + 1) for each in geneExp
        ]
        all_tpm_list = row + locus_result['dev_expression_tpm']
        locus_result['max_tpm'] = np.ceil(max(all_tpm_list))
    return locus_result


def fetch_sequence(table, chr, start_pos, end_pos):
    cmd = "python {script} \
    --refer /data/data/wheat/reference/Chinese_Spring_v1.0.fasta \
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
    print(cmd)
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
    else:
        return pd.DataFrame([])
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


def fetch_lnc_pcg_pairs(options):
    print(options)
    genes = [each for each in options['genes'] if each]
    if genes:
        mrna_res = RnaNeighbor.query.filter(
            RnaNeighbor.mRNA_gene.in_(genes)).all()
        lnc_res = RnaNeighbor.query.filter(
            RnaNeighbor.lncRNA_gene.in_(genes)).all()
    else:
        chrom = options['chrom']
        start = options['start']
        end = options['end']
        mrna_res = RnaNeighbor.query.filter(RnaNeighbor.chrom == chrom,
                                            RnaNeighbor.mRNA_start >= start,
                                            RnaNeighbor.mRNA_end <= end).all()
        lnc_res = RnaNeighbor.query.filter(
            RnaNeighbor.chrom == chrom, RnaNeighbor.lncRNA_start >= start,
            RnaNeighbor.lncRNA_end <= end).all()
    return mrna_res + lnc_res


def fetch_pcg_exp(geneList: List[str], sampleList: List[str]):
    query_out = GeneExpression.query.filter(
        GeneExpression.gene_id.in_(geneList),
        GeneExpression.tissue.in_(sampleList)).all()
    return [item.as_dict() for item in query_out]


def fetch_lnc_exp(geneList: List[str], sampleList: List[str]):
    query_out = LncExpression.query.filter(
        LncExpression.gene_id.in_(geneList),
        LncExpression.tissue.in_(sampleList)).all()
    return [item.as_dict() for item in query_out]


def normalized_tpm(tpm):
    return np.log2(tpm + 1)


def fetch_exp_item(genes, expItems):
    expList = []
    for gene in genes:
        gene_exp_list = []
        for exp_i in expItems:
            if exp_i['gene_id'] == gene:
                gene_exp_list.append(normalized_tpm(exp_i['tpm']))
        expList.append(gene_exp_list)
    return expList


def pearson_cor(mrna, lncrna, mrnaExp, lncExp, mrna_lnc_pair):
    exp_product = list(product(mrnaExp, lncExp))
    results = []
    for n, gene_pair in enumerate(product(mrna, lncrna)):
        gene_pair_str = '-'.join(gene_pair)
        if gene_pair_str in mrna_lnc_pair:
            pcc, pval = stats.pearsonr(exp_product[n][0], exp_product[n][1])
            if pcc is np.nan:
                pcc = 0
                pval = 1
            results.append({
                "mRNA": gene_pair[0],
                "lncRNA": gene_pair[1],
                "pcc": round(pcc, 3),
                "p-value": pval
            })
    return results


def echarts_cluster_heatmap_data(geneList, expItems):
    Z = complete(pdist(expItems))
    cluster_order = leaves_list(Z)
    reorder_exp = [expItems[i] for i in cluster_order]
    reorder_gene = [geneList[i] for i in cluster_order]
    heatmap_data = []
    for i, expList_i in enumerate(reorder_exp):
        for j, tpm_i in enumerate(expList_i):
            heatmap_data.append([j, i, tpm_i])
    return reorder_gene, heatmap_data