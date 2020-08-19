from . import mapping
from .actions import run_bsa, compare_info, fetch_task_info
from flask import render_template, request, jsonify, flash, url_for, redirect
from flask_login import current_user
import json
from app.utils import redis_task, fetch_vcf


def current_username():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return 'anonymous'


@mapping.route('/bsa-base/', methods=['GET'])
def bsa_base():
    name = current_username()
    pub_samples, private_samples = fetch_vcf(name)
    if current_user.is_authenticated:
        return render_template('mapping/mapping_bsa_base.html',
                               pub_samples=pub_samples,
                               pri_samples=private_samples)
    else:
        return render_template('mapping/mapping_bsa_anony_choose.html')


@mapping.route('/bsa-base-anony/<task_id>', methods=['GET'])
def bsa_base_anony(task_id):
    name = current_username()
    pub_samples, _ = fetch_vcf(name)
    if task_id == 'no':
        return render_template('mapping/mapping_bsa_base.html',
                               pub_samples=pub_samples,
                               pri_samples=[])
    else:
        task_info = fetch_task_info(task_id)
        if task_info:
            if task_info.task_status == 'running':
                flash('Your Data is still under processing, please wait.',
                      'warning')
                return redirect(url_for('mapping.bsa_base_upload'))
            else:
                return render_template('mapping/mapping_bsa_base.html',
                                       pub_samples=pub_samples,
                                       pri_samples=[])
        else:
            flash('Invalid upload id, please check.', 'warning')
            return redirect(url_for('mapping.bsa_base_upload'))


@mapping.route('/bsa-base-upload/', methods=['GET'])
def bsa_base_upload():
    return render_template('mapping/mapping_bsa_anony_upload.html')


@mapping.route('/bsa/', methods=['GET'])
def bsa():
    name = current_username()
    pub_samples, private_samples = fetch_vcf(name)
    return render_template('mapping/mapping_bsa.html',
                           pub_samples=pub_samples,
                           pri_samples=private_samples)


@mapping.route('/compare/group/', methods=['GET'])
def compare_group():
    name = current_username()
    pub_samples, private_samples = fetch_vcf(name)
    return render_template('mapping/compare_group.html',
                           pub_samples=pub_samples,
                           pri_samples=private_samples)


@mapping.route('/bsa/run/', methods=['GET', 'POST'])
def fetch_bsa():
    if request.method == 'POST':
        info = request.form['info']
        task = run_bsa.delay(info)
        redis_task.push_task(current_username(), task.id)
        return jsonify({'msg': 'ok', 'task_id': task.id})


@mapping.route('/compare/run/', methods=['POST'])
def fetch_compare():
    if request.method == 'POST':
        info = request.form['info']
        info = json.loads(info)
        task = compare_info.delay(info)
        redis_task.push_task(current_username(), task.id)
        return jsonify({'msg': 'ok', 'task_id': task.id})
    return jsonify({'msg': 'method not allowed'})
