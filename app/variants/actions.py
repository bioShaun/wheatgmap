import os
import re
import json
import delegator
from pathlib import Path
from typing import List, Optional
from app.utils import processor, parseInput
from settings import Config, basedir
from app.app import celery

gene_bed_file = Config.GENE_POS
UPLOAD_PATH = os.path.join(basedir, 'app', 'static', 'download')
ANN_PATH = os.path.join(UPLOAD_PATH, 'vcf_ann')
VAR_DENSITY_PATH = os.path.join(UPLOAD_PATH, 'var_density')


@celery.task
def snp_info(info):
    tmp_param = {
        'not_a_group_id': info['group'],
        'group_names': ["not_a_group_id"]
    }
    genes = info.get('gene_list')
    if genes:
        gene_list = parseInput(genes)
        if len(gene_list) == 0:
            return {'task': 'snp_info', 'result': {'header': [], 'body': []}}
        tmp_param.update({'gene_id': gene_list})
    else:
        tmp_param.update({
            'chrom': info['chr'],
            'chrom_start': info['pos_start'],
            'chrom_end': info['pos_end']
        })
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
        return {
            'task': 'snp_info',
            'result': {
                'header': head_data,
                'body': body_data
            }
        }
    return {'task': 'snp_info', 'result': {'header': [], 'body': []}}


@celery.task
def snp_info_by_chr(info):
    tmp_param = {
        'not_a_group_id': info['group'],
        'group_names': ["not_a_group_id"]
    }
    genes = info.get('gene_list')
    if genes:
        gene_list = parseInput(genes)
        if len(gene_list) == 0:
            return {'task': 'snp_info', 'result': {'header': [], 'body': []}}
        tmp_param.update({'gene_id': gene_list})
    else:
        tmp_param.update({
            'chrom': info['chr'],
            'chrom_start': info['pos_start'],
            'chrom_end': info['pos_end']
        })
    cmd = "snpInf-bychr \
            --gene_bed {gene_bed} \
            --vcf_ann_dir {vcf_ann_dir} \
            --vcf_dir {vcf_table_dir} \
            --outdir {outdir} \
            --parameters '{param}'".format(
        vcf_table_dir=Config.VCF_TABLE_BYCHR_PATH,
        vcf_ann_dir=Config.VCF_ANN_BYCHR_PATH,
        gene_bed=gene_bed_file,
        param=json.dumps(tmp_param),
        outdir=ANN_PATH,
    )
    print(cmd)
    result = processor.shRun(cmd)
    if result:
        head_data = result[0].split('\t')
        body_data = [row.split('\t') for row in result[1:]]
        return {
            'task': 'snp_info',
            'result': {
                'header': head_data,
                'body': body_data
            }
        }
    return {'task': 'snp_info', 'result': {'header': [], 'body': []}}


def window_number_format(number: int) -> str:
    megabase = 1000 * 1000
    kilobase = 1000
    if number >= megabase:
        return f"{number / megabase}M"
    elif number >= kilobase:
        return f"{int(number / kilobase)}K"
    else:
        return str(number)


def va_density_compare_dir(sample_list: List[str], min_depth: int, window: int,
                           min_alt_freq: float, step: Optional[int],
                           outdir: str) -> Path:
    sample_name = '_'.join(sample_list)
    window_str = f"window_{window_number_format(window)}"
    if step:
        step_str = f"-step_{window_number_format(step)}"
    else:
        step_str = ""
    folder_name = f"{sample_name}-depth_{min_depth}-alt_freq_{min_alt_freq}-{window_str}{step_str}"
    out_folder = Path(outdir) / folder_name
    return out_folder


def launch_var_density_plot(sample_list: List[str],
                            min_depth: int = 1,
                            window: int = 1000_000,
                            min_alt_freq: float = 0,
                            step: Optional[int] = None):
    res_dir = va_density_compare_dir(sample_list=sample_list,
                                     min_depth=min_depth,
                                     window=window,
                                     step=step,
                                     min_alt_freq=min_alt_freq,
                                     outdir=VAR_DENSITY_PATH)
    samples = ','.join(sample_list)
    plot_cmd = (f"varDensityCompare {samples} "
                f"{Config.VCF_TABLE_BYCHR_PATH} "
                f"{Config.CHROM_SIZE} "
                f"{res_dir} "
                f"--min-depth {min_depth} "
                f"--window {window} "
                f"--min-alt-freq {min_alt_freq}")
    print(plot_cmd)
    delegator.run(plot_cmd)
    zip_cmd = f'cd {VAR_DENSITY_PATH} && zip -r {res_dir.name}.zip {res_dir.name}'
    print(zip_cmd)
    delegator.run(zip_cmd)
    return re.sub(r'\S+wheat.*/app', '', str(res_dir))