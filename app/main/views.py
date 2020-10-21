from app.auth.models import Data
from . import main
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required
import requests

FLOWER_URL = 'http://127.0.0.1:5555'


@main.route('/')
def index():
    # data_info = Data.query.filter_by(opened=1, sign=0).order_by(
    #     Data.create_time.desc()).limit(10).all()
    # test
    data_info = Data.query.filter_by(sign=0).order_by(
        Data.create_time.desc()).limit(5).all()
    wgs_count = Data.query.filter_by(opened=1, sign=0, type="WGS").count()
    wes_count = Data.query.filter_by(opened=1, sign=0, type="WES").count()
    rna_count = Data.query.filter_by(opened=1, sign=0, type="RNAseq").count()
    return render_template('cover.html',
                           data_info=data_info,
                           wgs_count=wgs_count,
                           wes_count=wes_count,
                           rna_count=rna_count)
    #return redirect(url_for('data.samples'))


@main.route('/task/result/<task_id>', methods=['GET'])
def show_result(task_id):
    return render_template('celery_task.html',
                           task_id=task_id,
                           state='pending')


@main.route('/task/result/', methods=['POST'])
def celery_task():
    if request.method == 'POST':
        task_id = request.form['task_id']
        url = '{root_url}/api/task/result/{id}'.format(root_url=FLOWER_URL,
                                                       id=task_id)
        reply = requests.get(url).json()
        if reply['state'] == 'SUCCESS':
            task = reply['result']['task']
            result = reply['result']['result']
            return jsonify({'msg': 'ok', 'task': task, 'result': result})
        elif reply['state'] == 'PENDING':
            return jsonify({'msg': 'pending'})
        else:
            return jsonify({'msg': 'error'})


@main.route('/vcf-upload/<dest>', methods=['GET'])
def anony_upload(dest):
    return render_template('anony_upload.html', dest=dest)


@main.route('/choose-data/<dest>', methods=['GET'])
def anony_choose(dest):
    return render_template('anony_choose.html', dest=dest)
