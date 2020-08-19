# coding=utf-8
import json
from . import variants
from .actions import snp_info, snp_info_by_chr
from flask import render_template, jsonify, request, session, flash, redirect, url_for
from app.auth.models import Data, TaskInfo
from app.utils import parseInput, redis_task, fetch_vcf, fetch_vcf_by_task
from flask_login import current_user, login_required


def current_username():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return 'anonymous'


@variants.route('/query/sample/')
def query_sample():
    name = current_username()
    pub_samples, private_samples = fetch_vcf(name)
    if current_user.is_authenticated:
        return render_template('variants/query_sample.html',
                               pub_samples=pub_samples,
                               pri_samples=private_samples)
    else:
        return render_template('variants/query_sample_anony_choose.html')


@variants.route('/query-anony/sample/<task_id>', methods=['GET'])
def query_sample_anony(task_id):
    name = current_username()
    pub_samples, _ = fetch_vcf(name)
    if task_id == 'no':
        return render_template('variants/query_sample.html',
                               pub_samples=pub_samples,
                               pri_samples=[])
    else:
        task_info = TaskInfo.findByTaskId(task_id)
        if task_info:
            if task_info.task_status == 'running':
                flash('Your Data is still under processing, please wait.',
                      'warning')
                return redirect(url_for('variants.query_sample_upload'))
            elif task_info.task_status == 'finished':
                upload_samples = fetch_vcf_by_task(task_info.task_id)
                return render_template('variants/query_sample.html',
                                       pub_samples=pub_samples,
                                       pri_samples=upload_samples)
            else:
                flash('Upload Failed, please try again.', 'error')
                return redirect(url_for('mapping.query_sample_upload'))
        else:
            flash('Invalid upload id, please check.', 'warning')
            return redirect(url_for('mapping.query_sample_upload'))


@variants.route('/query/sample-upload/', methods=['GET'])
def query_sample_upload():
    return render_template('variants/query_sample_anony_upload.html')


@variants.route('/query/result/', methods=['POST'])
def fetch_query_result():
    if request.method == 'POST':
        info = request.form['info']
        info = json.loads(info)
        task = snp_info_by_chr.delay(info)
        if current_user.is_authenticated:
            user_name = current_user.username
        else:
            user_name = 'anonymous'
        redis_task.push_task(user_name, task.id)
        return jsonify({'msg': 'ok', 'task_id': task.id})
    return jsonify({'msg': 'method not allowed'})
