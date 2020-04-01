# -*- coding: utf-8 -*-
import json
from . import data
from app.auth.models import Data, User, Variety, Comment, VarietyDetail
from flask_login import login_required, current_user
from flask import render_template, request, jsonify, redirect, url_for

@data.route('/samples/')
def samples():
    samples = Data.query.filter_by(opened=1, sign=0).all()
    return render_template('/data/data.html', samples=samples)


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
        institute = user.institute
        phone = user.phone
        email = user.email
    else:
        exists = False
        institute, phone, email = ('', '', '')
    return render_template('data/user.html', username=username, institute=institute, phone=phone, email=email, exists=exists)


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

