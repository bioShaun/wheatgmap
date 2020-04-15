# coding:utf-8
import os
import json
import time
from . import auth
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Data, VarietyDetail
from app.exetensions import login_manager
from .forms import RegisterForm, LoginForm, EditForm
from .actions import fetch_vcf_samples, async_fetch_vcf_samples
from flask import render_template, \
    request, redirect, url_for, flash, jsonify, session
from settings import Config, basedir
from werkzeug import secure_filename
from app.mail import send_mail
from app.utils import redis_task, vcfValidator
from pathlib import PurePath


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=int(id)).first()


'''
@auth.before_app_request
def before_request():
    if not current_user.is_authenticated \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and not current_user.is_active \
            and request.endpoint != 'static' \
            and request.endpoint[:5] != 'data.' \
            and request.endpoint[:5] != 'main.' \
            and request.endpoint[:6] != 'tools.':
            #and request.endpoint[:9] != 'variants.' \
            #and request.endpoint[:11] != 'expression.':
        return redirect(url_for('auth.unconfirmed'))



@auth.before_app_first_request
def create_test_table():
    Snptable.query.delete()
    tables = [Snptable(tablename='snp_mRNA_ann_table',
                       tabletype='snp',
                       owner='chencheng'),
              Snptable(tablename='expr_gene_tmp_pos',
                       tabletype='expr',
                       owner='chencheng')]
    db.session.add_all(tables)
    db.session.commit()
'''


@auth.route('/unconfirmed/')
def unconfirmed():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    mail_addr = Config.MAIL_MAP.get(current_user.email.split('@')[1], '')
    return render_template('auth/unconfirmed.html', mail=mail_addr)


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>/')
def confirm(token):
    user = User.confirm(token)
    if user:
        if user.is_active:
            flash('you have update your email infomation.', 'success')
            login_user(user)
            return redirect(url_for('main.index'))
        if not user.is_active:
            user.update(is_active=True)
            flash('you have confirm your account. Thanks!', 'success')
            return redirect(url_for('main.index'))
    else:
        flash('the confirmation link is invalid.', 'danger')
    return redirect(url_for('main.index'))


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = EditForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data,
                    institute=form.institute.data,
                    phone=form.telephone.data,
                    pub_phone=form.pub_phone.data,
                    research=form.research.data,
                    profile=form.profile.data,
                    photo=form.photo.data)
        user.save()
        token = user.generate_confirmation_token()
        send_mail(user.email,
                  'Confirm Your Account',
                  'mail/confirm',
                  user=user,
                  token=token)
        flash(
            'Thanks your register. A confirm email has been sent to your email',
            'success')
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/edit.html',
                           form=form,
                           defaultPhoto=Config.DEFAULT_USER_PHOTO)


@auth.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit():
    if not current_user.photo:
        current_user.photo = Config.DEFAULT_USER_PHOTO
        current_user.save()
    form = EditForm(username=current_user.username,
                    email=current_user.email,
                    institute=current_user.institute,
                    telephone=current_user.phone,
                    pub_phone=current_user.pub_phone,
                    research=current_user.research,
                    profile=current_user.profile)
    if form.validate_on_submit():
        current_user.institute = form.institute.data
        current_user.phone = form.telephone.data
        current_user.pub_phone = form.pub_phone.data
        current_user.research = form.research.data
        current_user.profile = form.profile.data
        current_user.save()
        flash('User Information Updated.', 'success')
        return redirect(url_for('auth.edit'))
    return render_template('auth/edit.html', form=form, user=current_user)


@auth.route('/upload_photo/', methods=['GET', 'POST'])
@login_required
def upload_photo():
    for f in request.files.getlist('file'):
        print(f)
        fileSfx = PurePath(f.filename).suffix
        timestamp = str(time.time()).replace('.', '-')
        filename = f'{timestamp}-{f.filename}'
        url = os.path.join(Config.UPLOADED_PHOTOS_DEST, filename)
        filePath = f'{basedir}/app/{url}'
        print(filePath)
        f.save(filePath)
        if not current_user.is_anonymous:
            oldUrl = current_user.photo
            if oldUrl != Config.DEFAULT_USER_PHOTO:
                oldFilePath = f'{basedir}/app/{oldUrl}'
                os.remove(oldFilePath)
            current_user.photo = url
            current_user.save()
        return jsonify({"msg": "success", 'PhotoUrl': url})


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            session['username'] = form.user.username
            flash('You are loggin in.', 'success')
            redicret_url = request.args.get('next') or url_for('auth.account')
            return redirect(redicret_url)
    return render_template('auth/login.html', form=form)


@auth.route('/account/', methods=['GET'])
@login_required
def account():
    return render_template('auth/account.html')


@auth.route('/tasks/', methods=['GET'])
@login_required
def tasks():
    my_tasks = redis_task.fetch_task(current_user.username)
    variety = VarietyDetail.query.filter_by(provider=current_user.id).all()
    return render_template(
        "auth/tasks.html",
        tasks=my_tasks,
        variety_items=variety,
    )


@auth.route('/upload/', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'vcf_file' not in request.files:
            return jsonify({'msg': 'No vcf gzip part', 'table': []})
        vcf_type = request.form['vcf_type']
        vcf_file = request.files['vcf_file']
        if vcf_file.filename == '':
            return jsonify({'msg': 'No selected file', 'table': []})

        if vcf_file and vcf_file.filename.rsplit('/')[-1][-6:] == 'vcf.gz':
            # add timestamp
            filename = '_'.join(
                [str(int(time.time())),
                 secure_filename(vcf_file.filename)])
            filepath = os.path.join(Config.VCF_FILE_PATH, filename)
            vcf_file.save(filepath)
            vcf_check_msg = vcfValidator(filepath)
            if vcf_check_msg:
                return jsonify({'msg': vcf_check_msg, 'table': []})
            if os.stat(filepath).st_size > 1 * 1000:
                task = async_fetch_vcf_samples.delay(filename,
                                                     current_user.username,
                                                     vcf_type)
                redis_task.push_task(current_user.username, task.id)
                return jsonify({'msg': 'async', 'task_id': task.id})
            else:
                result = fetch_vcf_samples(filename, vcf_type)
                # write to mysql
                for each in result:
                    row = Data(tc_id=each[0],
                               provider=current_user.username,
                               sample_name=each[1],
                               type=vcf_type)
                    row.save()
                return jsonify({'msg': 'ok', 'table': result})
        return jsonify({'msg': 'check upload file(only *.vcf.gz suffix)'})


""" @auth.route('/samples/', methods=['GET'])
@login_required
def samples():
    #samples = Data.query.filter_by(provider=current_user.username).all()
    return render_template("auth/samples.html") """


@auth.route('/userData/', methods=['GET'])
@login_required
def userData():
    stat = {}
    pr_vcf = 0
    pu_vcf = 0
    pr_sample = len(
        Data.query.filter_by(opened=0, sign=0,
                             provider=current_user.username).all())
    pu_sample = len(
        Data.query.filter_by(opened=1, sign=0,
                             provider=current_user.username).all())
    stat = {
        'pr_vcf': pr_vcf,
        'pu_vcf': pu_vcf,
        'pr_sample': pr_sample,
        'pu_sample': pu_sample
    }
    #samples = Data.query.filter_by(provider=current_user.username).all()
    return render_template("auth/userData.html", stat=stat)


@auth.route('/fetch_samples/', methods=['GET', 'DELETE', 'PUT', 'POST'])
@login_required
def fetch_samples():
    if request.method == 'GET':
        result = []
        samples = Data.query.filter_by(provider=current_user.username,
                                       sign=0).all()
        for sample in samples:
            result.append({
                'opened': sample.opened,
                'tc_id': sample.tc_id,
                'sample_name': sample.sample_name,
                'type': sample.type,
                'scientific_name': sample.scientific_name,
                'variety_name': sample.variety_name,
                'high_level_tissue': sample.high_level_tissue,
                'high_level_age': sample.high_level_age,
                'treatments': sample.treatments,
                'tissue': sample.tissue,
                'age': sample.age,
                'stress_disease': sample.stress_disease,
                'dol': sample.dol,
                'bulked_segregant': sample.bulked_segregant,
                'mixed_sample': sample.mixed_sample,
                'mutant_transgenosis': sample.mutant_transgenosis,
                'other_inf': sample.other_inf
            })
        return jsonify(result)
    elif request.method == 'DELETE':
        ids = request.form['ids']
        id_serise = ids.split(',')
        for each in id_serise:
            sample = Data.query.filter_by(tc_id=each).first()
            sample.update(sign=1)
        return jsonify({'msg': 'ok'})
    elif request.method == 'PUT':
        info = request.form['data']
        info = json.loads(info)
        sample = Data.query.filter_by(tc_id=info['id']).first()
        del (info['id'])
        sample.update(**info)
        return jsonify({'msg': 'ok'})
    elif request.method == 'POST':
        ids = request.form['ids']
        action = request.form['action']
        id_serise = ids.split(',')
        if action == 'pub':
            for id in id_serise:
                sample = Data.query.filter_by(tc_id=id).first()
                sample.update(opened=1)
        else:
            for id in id_serise:
                sample = Data.query.filter_by(tc_id=id).first()
                sample.update(opened=0)
        return jsonify({'msg': 'ok'})


@auth.route('/confirm/')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,
              'Confirm Your Account',
              'mail/confirm',
              user=current_user,
              token=token)
    flash('A new confirmation email has been sent to you by email.', 'success')
    return redirect(url_for('main.index'))
