# -*- coding: utf-8 -*-
import os
from . import expression
import json
import re
from werkzeug import secure_filename
from flask import render_template, request, jsonify
from .actions import run_enrich, async_run_enrich, fetch_expression_data, fetch_expression_plot_data
from settings import basedir
from app.utils import parseInput, fetch_sample, redis_task
from flask_login import login_required, current_user

UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'download')
ENRICH_SPECIES = ('Arabidopsis thaliana (thale cress)',
                  'Oryza sativa japonica (Japanese rice)')


@expression.route('/enrich/', methods=['GET'])
def enrichment():
    return render_template('expression/enrichment.html',
                           species=ENRICH_SPECIES)


@expression.route('/search/gene/')
def expression_by_gene():
    samples = fetch_sample(table='iwgsc_refseq', fixed_column_num=2)
    return render_template('expression/show_by_gene.html', samples=samples)


@expression.route('/search/result/', methods=['POST'])
def fetch_expression_info():
    if request.method == 'POST':
        info = request.form['info']
        info = json.loads(info)
        group = info['group']
        genes = re.split(r'[\s,]', info['gene_name'].strip())
        datas = {}
        for gene in genes:
            data = fetch_expression_data(gene, group)
            datas[gene] = data
        if len(datas) == 1 and len(datas[gene]) == 0:
            return jsonify({'msg': 'not search {0} in database!'.format(gene)})

        return jsonify({'msg': 'ok', 'data': datas})


@expression.route('/enrich/table/', methods=['POST'])
def fetch_enrich_table():
    if request.method == 'POST':
        specie = request.form['specie']
        gene_list = request.form.get('gene_list')
        if gene_list:
            gene_list = parseInput(gene_list)
            task = async_run_enrich.delay(specie, gene_list)
            redis_task.push_task(current_user.username, task.id)
            return jsonify({'msg': 'async', 'task_id': task.id})
            # result = run_enrich(specie, gene_list)
            # if len(result['body']) == 0:
            #     return jsonify({'msg': 'no enrich on your gene list.', 'result': {}})
            # return jsonify({'msg': 'ok', 'result': result})
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, 'enrich', filename))
        task = async_run_enrich.delay(specie, filename)
        return jsonify({'msg': 'async', 'task_id': task.id})


@expression.route('/pca/')
def expression_pca():
    samples = fetch_sample(table='iwgsc_refseq', fixed_column_num=2)
    return render_template('expression/pca.html', samples=samples)


@expression.route('/pca/result/', methods=['POST'])
def fetch_expression_plot():
    if request.method == 'POST':
        info = json.loads(request.form['info'])
        samples = info['group']
        result = fetch_expression_plot_data(samples)
        return jsonify({'msg': 'ok', 'table': result})
    return jsonify({'msg': 'error', 'table': []})
