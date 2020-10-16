import json
import uuid
from datetime import datetime
from flask import render_template, request, jsonify, flash, url_for, redirect
from flask_login import current_user
from . import mapping
from .actions import run_bsa, compare_info, launch_var_filter
from app.utils import redis_task, fetch_vcf, fetch_vcf_by_task, tasks_status
from app.auth.models import TaskInfo
from pathlib import PurePath


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
        return redirect(url_for('main.anony_choose', dest='bsa-mapping'))


@mapping.route('/var-filter/', methods=['GET'])
def var_filter():
    name = current_username()
    pub_samples, private_samples = fetch_vcf(name)
    if current_user.is_authenticated:
        return render_template('mapping/var_filter.html',
                               pub_samples=pub_samples,
                               pri_samples=private_samples)
    else:
        return redirect(url_for('main.anony_choose', dest='var-filter'))


@mapping.route('/var-filter/launch/', methods=['POST'])
def var_density_plot():
    if request.method == 'POST':
        info = request.form['info']
        print(info)
        out_plot = launch_var_filter(info)
        out_file = PurePath(out_plot).parent.parent / 'variantFilter.zip'
        if out_plot:
            return jsonify({
                'msg': 'ok',
                'out_plot': str(out_plot),
                'out_file': str(out_file)
            })
        return jsonify({'msg': 'failed'})


@mapping.route('/bsa-base-anony/<task_id>', methods=['GET'])
def bsa_base_anony(task_id):
    name = current_username()
    pub_samples, _ = fetch_vcf(name)
    if task_id == 'no':
        return render_template('mapping/mapping_bsa_base.html',
                               pub_samples=pub_samples,
                               pri_samples=[])
    else:
        task_info = tasks_status(task_id)
        if task_info:
            if task_info == 'all_done':
                upload_samples = fetch_vcf_by_task(task_id)
                return render_template('mapping/mapping_bsa_base.html',
                                       pub_samples=pub_samples,
                                       pri_samples=upload_samples)
            else:
                flash(task_info, 'warning')
                return redirect(
                    url_for('main.anony_upload', dest='bsa-mapping'))
        else:
            flash('Invalid upload id, please check.', 'warning')
            return redirect(url_for('main.anony_upload', dest='bsa-mapping'))


@mapping.route('/var-filter-anony/<task_id>', methods=['GET'])
def var_filter_anony(task_id):
    name = current_username()
    pub_samples, _ = fetch_vcf(name)
    if task_id == 'no':
        return render_template('mapping/var_filter.html',
                               pub_samples=pub_samples,
                               pri_samples=[])
    else:
        task_info = tasks_status(task_id)
        if task_info:
            if task_info == 'all_done':
                upload_samples = fetch_vcf_by_task(task_id)
                return render_template('mapping/var_filter.html',
                                       pub_samples=pub_samples,
                                       pri_samples=upload_samples)
            else:
                flash(task_info, 'warning')
                return redirect(url_for('main.anony_upload',
                                        dest='var-filter'))
        else:
            flash('Invalid upload id, please check.', 'warning')
            return redirect(url_for('main.anony_upload', dest='var-filter'))


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
    if current_user.is_authenticated:
        return render_template('mapping/compare_group.html',
                               pub_samples=pub_samples,
                               pri_samples=private_samples)
    else:
        return redirect(url_for('main.anony_choose', dest='var-by-group'))


@mapping.route('/compare-anony/group/<task_id>', methods=['GET'])
def compare_group_anony(task_id):
    name = current_username()
    pub_samples, _ = fetch_vcf(name)
    if task_id == 'no':
        return render_template('mapping/compare_group.html',
                               pub_samples=pub_samples,
                               pri_samples=[])
    else:
        task_info = tasks_status(task_id)
        if task_info:
            if task_info == 'all_done':
                upload_samples = fetch_vcf_by_task(task_id)
                return render_template('mapping/compare_group.html',
                                       pub_samples=pub_samples,
                                       pri_samples=upload_samples)
            else:
                flash(task_info, 'warning')
                return redirect(
                    url_for('main.anony_upload', dest='var-by-group'))
        else:
            flash('Invalid upload id, please check.', 'error')
            return redirect(url_for('main.anony_upload', dest='var-by-group'))


@mapping.route('/bsa/run/', methods=['GET', 'POST'])
def fetch_bsa():
    if request.method == 'POST':
        username = current_username()
        info = request.form['info']
        job_name = request.form['jobName']
        task_id = str(uuid.uuid1())
        task = run_bsa.delay(info, task_id)
        redis_task.push_task(current_username(), task.id)
        bsa_task = TaskInfo(task_name=job_name,
                            task_type='gene mapping',
                            task_status='running',
                            task_id=task_id,
                            username=username,
                            redis_id=task.id,
                            create_time=datetime.now())
        bsa_task.save()
        return jsonify({'msg': 'ok', 'task_id': task.id, 'username': username})
    return jsonify({'msg': 'method not allowed'})


@mapping.route('/bsa/launched/<task_id>', methods=['GET'])
def bsa_launched(task_id):
    return render_template('mapping/mapping_launched.html', task_id=task_id)


@mapping.route('/bsa/search/<task_id>', methods=['GET'])
def bsa_search(task_id):
    if task_id != 'none':
        task_info = TaskInfo.findByRedisId(task_id)
        if task_info:
            if task_info.task_status == 'finished':
                return redirect(url_for('main.show_result', task_id=task_id))
            else:
                flash('Your task is under processing, please wait.', 'warning')
                return render_template('mapping/mapping_search.html',
                                       task_id='none')
        else:
            flash('Invalid task id, please check.', 'warning')
            return render_template('mapping/mapping_search.html',
                                   task_id='none')
    else:
        return render_template('mapping/mapping_search.html', task_id='none')


@mapping.route('/compare/run/', methods=['POST'])
def fetch_compare():
    if request.method == 'POST':
        info = request.form['info']
        info = json.loads(info)
        task = compare_info.delay(info)
        redis_task.push_task(current_username(), task.id)
        return jsonify({'msg': 'ok', 'task_id': task.id})
    return jsonify({'msg': 'method not allowed'})
