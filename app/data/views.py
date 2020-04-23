# -*- coding: utf-8 -*-
import os
import json
import time
from . import data
from app.auth.models import Data, User, Variety, Comment, VarietyDetail, VarietyComment, VarietyFigureExample, DataFigure
from app.variety.forms import VarietyCommentForm
from flask_login import login_required, current_user
from flask import render_template, request, jsonify, redirect, url_for
from settings import Config, basedir


@data.route('/samples/')
def samples():
    samples = Data.query.filter_by(opened=1, sign=0).all()
    return render_template('/data/data.html', samples=samples)


@data.route('/samples/<tc_id>/', methods=['GET', 'POST'])
def dataDetail(tc_id):
    data = Data.query.filter_by(tc_id=tc_id).first()
    comments = VarietyComment.query.filter_by(variety=data.id,
                                              comment_type="data_comm").all()
    if data.variety_name:
        va_id = int(data.variety_name.replace('TC-Va-', ""))
        va_name = VarietyDetail.query.get(va_id).variety_name
    else:
        va_name = ""
    figs = data.figures
    leftFigNum = 10 - len(figs)
    exampleFig = VarietyFigureExample()
    provider_obj = User.query.filter_by(username=data.provider).first()
    isProvider = current_user.id == provider_obj.id

    form = VarietyCommentForm(content="")
    if form.validate_on_submit():
        if current_user.is_anonymous:
            flash('You need to Login first.', "error")
            return redirect(url_for('auth.login'))
        else:
            provider = current_user.id
            v_comment = VarietyComment(
                content=form.content.data,
                provider=provider,
                variety=data.id,
                comment_type="data_comm",
            )
            v_comment.save()
            flash('Add a new comment.', 'success')
            return redirect(url_for('data.dataDetail', tc_id=tc_id))
    return render_template('/data/data_view.html',
                           data=data,
                           comments=comments,
                           form=form,
                           figs=figs,
                           leftFigNum=leftFigNum,
                           exampleFig=exampleFig,
                           isProvider=isProvider,
                           va_name=va_name)


@data.route('/upload-img/<data_id>/', methods=['POST'])
@login_required
def upload_img(data_id):
    for f in request.files.getlist('file'):
        timestamp = str(time.time()).replace('.', '-')
        filename = f'{timestamp}-{f.filename}'
        url = os.path.join(Config.IMG_PATH, filename)
        filePath = f'{basedir}/app/{url}'
        f.save(filePath)
        vaFig = DataFigure(url=url, data=data_id).save()
        return jsonify({"id": vaFig.id, 'figUrl': url})


@data.route('/del-img/<fig_id>/', methods=['GET'])
@login_required
def delete_img(fig_id):
    vaFig = DataFigure.query.get(fig_id)
    filePath = os.path.join(basedir, 'app', vaFig.url)
    if os.path.isfile(filePath):
        os.remove(filePath)
    vaFig.delete()
    return jsonify({"msg": "success"})


@data.route('/varieties/')
def variety():
    va = VarietyDetail.query.all()
    #print(va)
    return render_template('/data/variety.html', va=va)


@data.route('/user/<username>/')
def users(username):
    user = User.query.filter_by(username=username).first()
    if user:
        exists = True
    else:
        exists = False
    nameList = [user.first_name, user.middle_name, user.family_name]
    validNameList = [name for name in nameList if name]
    validName = ' '.join(validNameList)
    va = VarietyDetail.query.filter_by(provider=user.id).all()
    samples = Data.query.filter_by(opened=1, sign=0, provider=username).all()
    return render_template('data/user.html',
                           user=user,
                           exists=exists,
                           va=va,
                           default_photo=Config.DEFAULT_USER_PHOTO,
                           samples=samples,
                           validName=validName)


@data.route('/variety/<varietyname>/')
def varietys(varietyname):
    return render_template("data/show_variety.html", variety_name=varietyname)


@data.route('variety/comment/add/', methods=['POST'])
@login_required
def add_comment():
    if request.method == 'POST':
        content = request.form['content']
        parent_id = request.form['parent_id']
        comment = Comment(parent_id=parent_id,
                          content=content,
                          provider=current_user.username)
        comment.save()
        return redirect(url_for('data.comments', commentid=parent_id))


@data.route('/variety/comment/<commentid>/', methods=['GET'])
def comments(commentid):
    if request.method == 'GET':
        parent_comment = Variety.query.filter_by(id=int(commentid)).first()
        parent_content = parent_comment.content
        comments = Comment.query.filter_by(parent_id=commentid).all()
        return render_template('data/comment.html',
                               parent_content=parent_content,
                               parent_id=commentid,
                               comments=comments)


@data.route('/fetch_variety/', methods=['GET', 'POST'])
def fetch_variety():
    if request.method == 'GET':
        result = []
        variety_name = request.args.get('variety_name')
        comments = Variety.query.filter_by(variety_name=variety_name).all()
        for comment in comments:
            result.append({
                'id': comment.id,
                'variety_name': comment.variety_name,
                'content': comment.content,
                'provider': comment.provider,
                'create_time': comment.create_time
            })
        return jsonify(result)
    elif request.method == 'POST':
        variety_name = request.form['variety_name']
        variety_content = request.form['variety_content']
        provider = current_user.username
        comment = Variety(variety_name=variety_name,
                          content=variety_content,
                          provider=provider)
        comment.save()
        return jsonify({'msg': 'ok'})
