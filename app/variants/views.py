# coding=utf-8
import json
from . import variants
from .actions import snp_info, snp_info_by_chr
from flask import render_template, jsonify, request, session
from app.auth.models import Data
from app.utils import parseInput, redis_task
from flask_login import current_user, login_required

@variants.route('/query/sample/')
def query_sample():
    pub_data = Data.query.filter(Data.opened==1, Data.sign==0).all()
    if pub_data:
        pub_samples = ['.'.join([each.tc_id,each.sample_name]) for each in pub_data]
    else:
        pub_samples = []

    if current_user.is_authenticated:
        user_name = current_user.username
    else:
        user_name = None
    
    #username = session.get('username')
    if user_name:
        private_data = Data.query.filter_by(provider=user_name, opened=0, sign=0).all()
        private_samples = ['.'.join([each.tc_id,each.sample_name]) for each in private_data]
    else:
        private_samples = []
    return render_template('variants/query_sample.html', pub_samples=pub_samples, pri_samples=private_samples)


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

