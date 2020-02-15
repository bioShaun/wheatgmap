from . import mapping
from . actions import fetch_vcf, run_bsa, compare_info
from flask import render_template, url_for, request, jsonify, redirect
from flask_login import current_user, login_required
import requests
import json
from app.utils import redis_task

def current_username():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return 'anonymous'

@mapping.route('/bsa-base/', methods=['GET'])
def bsa_base():
    samples = fetch_vcf()
    return render_template('mapping/mapping_bsa_base.html',samples=samples)


@mapping.route('/bsa/', methods=['GET'])
def bsa():
    samples = fetch_vcf()
    return render_template('mapping/mapping_bsa.html',samples=samples)


@mapping.route('/compare/group/', methods=['GET'])
def compare_group():
    samples=fetch_vcf()
    return render_template('mapping/compare_group.html', samples=samples)

    
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
  
