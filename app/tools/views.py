import os
import json
import itertools
from . import tools
from .actions import fetch_blast_result, get_locus_result, \
    batch_query_gene, fetch_sequence, allowed_file, run_pca, \
        run_vcf, run_annotation, async_run_annotation, query_gene_by_pos
from flask import render_template, request, jsonify, session
from werkzeug import secure_filename
from settings import basedir, Config
from app.auth.models import Data
from flask_login import current_user

UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'download')
VCF_ANNOTATION_DATABASE = ('wheat.hclc.v1.1', 'wheat.tcuni.v1.1')


@tools.route('/blast/table/', methods=['POST'])
def fetch_blast_table():
    if request.method == 'POST':
        info = json.loads(request.form['info'])
        if ',' in info['genes']:
            gene_list1 = list(
                itertools.chain(*[each.split(',') for each in a.split()]))
        else:
            gene_list1 = info['genes'].split()
        gene_list2 = query_gene_by_pos(**info)
        gene_list = list(set(gene_list1 + gene_list2))
        if len(gene_list) == 0:
            return jsonify({
                'msg':
                'Can not find matched gene in input gene list or genome region.',
                'result': []
            })
        result = batch_query_gene(gene_list)
        if result:
            return jsonify({'msg': 'ok', 'result': result})
        return jsonify({
            'msg': 'not find in database or input too much (genes>1000).',
            'result': result
        })


@tools.route('/blast/')
def blast():
    return render_template('tools/blast.html')


@tools.route('/jbrowse/')
def jbrowse():
    return render_template('tools/jbrowse.html')


@tools.route('/gene/information/')
def gene_information():
    if request.args.get('gene', ''):
        genename = request.args['gene']
        blast_results = fetch_blast_result(genename)
        locus_result = get_locus_result(genename, blast_results)
        return render_template('tools/fetch_gene_information.html',
                               locus_result=locus_result)
    return render_template('tools/gene_information.html')


@tools.route('/sample/sequence/')
def get_sequence():
    #vcfDir = "/home/app/wheatDB/data/vcf_private_sample/"
    pub_data = Data.query.filter(Data.opened == 1, Data.sign == 0).all()
    if pub_data:
        pub_samples = [
            '.'.join([each.tc_id, each.sample_name]) for each in pub_data
        ]
    else:
        pub_samples = []

    if current_user.is_authenticated:
        user_name = current_user.username
    else:
        user_name = None

    #username = session.get('username')
    if user_name:
        private_data = Data.query.filter_by(provider=user_name,
                                            opened=0,
                                            sign=0).all()
        private_samples = [
            '.'.join([each.tc_id, each.sample_name]) for each in private_data
        ]
    else:
        private_samples = []
    #samples = [file[:-7] for file in os.listdir(vcfDir) if file[-6:] == 'vcf.gz']
    return render_template('tools/get_sequence.html',
                           pub_samples=pub_samples,
                           pri_samples=private_samples)


@tools.route('/pca/plot/')
def get_pca_plot():
    return render_template('tools/get_pca_plot.html')


@tools.route('/vcf/sequence/', methods=['POST'])
def fetch_sequence_by_vcf():
    if request.method == 'POST':
        info = request.form['info']
        info = json.loads(info)
        table = info['table']
        chr = info['chr']
        start_pos = info['start_pos']
        end_pos = info['end_pos']
        results = fetch_sequence(table, chr, start_pos, end_pos)
        if results:
            return jsonify({'msg': 'ok', 'text': results})
        return jsonify({
            'msg':
            'not fetch sequence by vcf file: {0}.vcf.gz'.format(table),
            'text':
            results
        })


@tools.route('/upload/expression/', methods=['POST'])
def upload_expression():
    if request.method == 'POST':
        if 'expression' not in request.files:
            return jsonify({'msg': 'No file part', 'table': []})
        file = request.files['expression']
        if file.filename == '':
            return jsonify({'msg': 'No selected file', 'table': []})

        sample_group_name = ""
        sample_group = request.files.get('sample_group', "")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, 'pca', filename))
            if sample_group and allowed_file(sample_group.filename):
                sample_group_name = secure_filename(sample_group.filename)
                sample_group.save(
                    os.path.join(UPLOAD_FOLDER, 'pca', sample_group_name))
                #print('save it {0}'.format(sample_group_name))
            result = run_pca(filename, sample_group_name)
            return jsonify({'msg': 'ok', 'table': result})
        return jsonify({'msg': 'error'})


@tools.route('/upload/vcf2pca/', methods=['POST'])
def structure_pca():
    if request.method == 'POST':
        if 'vcfile' not in request.files:
            return jsonify({'msg': 'No vcf gzip part', 'table': []})
        file = request.files['vcfile']
        if file.filename == '':
            return jsonify({'msg': 'No selected file', 'table': []})

        if file and file.filename.rsplit('/')[-1][-6:] == 'vcf.gz':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, 'pca', filename)
            file.save(filepath)
            result = run_vcf(filepath)
            if result:
                return jsonify({'msg': 'ok', 'table': result})
        return jsonify({'msg': 'error'})


@tools.route('/vcf/annotation/', methods=['GET'])
def vcf_annotation():
    return render_template('tools/annotation.html',
                           annotation_database=VCF_ANNOTATION_DATABASE)


@tools.route('/vcf/result/', methods=['POST'])
def fetch_annotation_result():
    if request.method == 'POST':
        annotation_database = request.form['annotation_database']
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, 'vcf_ann', filename)
        file.save(filepath)
        if os.stat(filepath).st_size > 100 * 1000 * 1000:
            task = async_run_annotation.delay(filename, annotation_database)
            return jsonify({'msg': 'async', 'task_id': task.id})
        result = run_annotation(filename, annotation_database)
        return jsonify({'msg': 'ok', 'result': result})
