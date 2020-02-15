import os
import json
from app.utils import processor, parseInput
from settings import Config, basedir
from app.app import celery

gene_bed_file = '/data/data/wheat/reference/gene.5kbupdown.window.bed'
UPLOAD_PATH = os.path.join(basedir, 'app', 'static', 'download')
ANN_PATH = os.path.join(UPLOAD_PATH, 'vcf_ann')

@celery.task
def snp_info(info):
    tmp_param = {'not_a_group_id': info['group'],
                 'group_names': ["not_a_group_id"]}
    genes = info.get('gene_list')
    if genes:
        gene_list = parseInput(genes)
        if len(gene_list) == 0:
            return {'task': 'snp_info', 'result': {'header':[], 'body':[]}}
        tmp_param.update({'gene_id': gene_list})
    else:
        tmp_param.update({'chrom': info['chr'],
                          'chrom_start': info['pos_start'], 
                          'chrom_end': info['pos_end']})
    cmd = "snpInf \
            --gene_bed {gene_bed} \
            --vcf_ann_file /data/wheatdb/data/vcf_private/snp.ann.table.pkl \
            --vcf_dir {vcf_table} \
            --outdir {outdir} \
            --parameters '{param}'".format(
            gene_bed=gene_bed_file,
            vcf_table=Config.VCF_TABLE_PATH,
            param=json.dumps(tmp_param),
            outdir=ANN_PATH,
            )
    print(cmd)
    result = processor.shRun(cmd)
    if result:
        head_data = result[0].split('\t')
        body_data = [row.split('\t') for row in result[1:]]
        return {'task': 'snp_info', 'result': {'header': head_data, 'body': body_data}}
    return {'task': 'snp_info', 'result': {'header':[], 'body':[]}}

