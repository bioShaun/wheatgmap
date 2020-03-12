from . import variety
from .forms import VarietyForm, VarietyCommentForm
from app.auth.models import VarietyDetail, VarietyComment
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, \
    request, redirect, url_for, flash, jsonify, session
from flask import jsonify

@variety.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    form = VarietyForm()
    if form.validate_on_submit():
        variety_item = VarietyDetail(
            variety_name=form.variety_name.data,
            variety_type=form.variety_type.data,
            geographic=form.geographic.data,
            country=form.country.data,
            province=form.province.data,
            affiliation=form.affiliation.data,
            basic_info_sup="",
            provider=current_user.id,
            flower_color=form.flower_color.data,
            leaf_color=form.leaf_color.data,
            protein_content=form.protein_content.data,
            starch_content=form.starch_content.data,
            salt=form.salt.data,
            high_temperature=form.high_temperature.data,
            low_temperature=form.low_temperature.data,
            sheath_blight=form.sheath_blight.data,
            fusarium=form.fusarium.data,
            total_erosion=form.total_erosion.data,
            powdery_mildew=form.powdery_mildew.data,
            leaf_rust=form.leaf_rust.data,
            leaf_blight=form.leaf_blight.data,
            stripe_rust=form.stripe_rust.data,
            spinal_rust=form.spinal_rust.data,
            smut=form.smut.data)
        variety_item.save()
        flash(
            f'Variety "{variety_item.variety_name}" has been added to database.',
            'success')
        return redirect(url_for('auth.tasks'))
    return render_template('variety/variety_edit.html', form=form, create=True)


@variety.route('/detail/<variety_id>/', methods=['GET', 'POST'])
def detail(variety_id):
    if str(variety_id).startswith('TC-Va'):
        variety_id = int(str(variety_id).split('-')[-1])
    variety_item = VarietyDetail.query.get(variety_id)
    variety_id = variety_item.id
    comments = VarietyComment.query.filter_by(variety=variety_id,
                                              comment_type="commnet").all()
    form = VarietyCommentForm(content="")
    if form.validate_on_submit():
        if current_user.is_anonymous:
            flash('You need to Login first.', "error")
            return redirect(url_for('auth.login'))
        else:
            provider = current_user.id
            v_comment = VarietyComment(content=form.content.data,
                                       provider=provider,
                                       variety=variety_id)
            v_comment.save()
            flash('Add a new comment.', 'success')
            return redirect(url_for('variety.detail', variety_id=variety_id))
    return render_template('variety/variety_view.html',
                           variety_item=variety_item,
                           comments=comments,
                           form=form)


@variety.route('/reply/<variety_id>/<commentId>/', methods=['GET', 'POST'])
def reply(variety_id, commentId):
    reply_content = request.json
    comment_reply = VarietyComment(content=reply_content['reply'],
                                   provider=current_user.id,
                                   variety=commentId,
                                   comment_type="reply")

    comment_reply.save()
    return jsonify({"success": True})


@variety.route('/update/<variety_id>/', methods=['GET', 'POST'])
@login_required
def update(variety_id):
    variety_item = VarietyDetail.query.get(variety_id)
    if current_user.id != variety_item.provider:
        flash('Not authorized!', 'warning')
        return redirect(url_for('auth.account'))    
    form = VarietyForm(variety_name=variety_item.variety_name,
                       variety_type=variety_item.variety_type,
                       geographic=variety_item.geographic,
                       country=variety_item.country,
                       province=variety_item.province,
                       affiliation=variety_item.affiliation,
                       basic_info_sup="",
                       flower_color=variety_item.flower_color,
                       leaf_color=variety_item.leaf_color,
                       protein_content=variety_item.protein_content,
                       starch_content=variety_item.starch_content,
                       salt=variety_item.salt,
                       high_temperature=variety_item.high_temperature,
                       low_temperature=variety_item.low_temperature,
                       sheath_blight=variety_item.sheath_blight,
                       fusarium=variety_item.fusarium,
                       total_erosion=variety_item.total_erosion,
                       powdery_mildew=variety_item.powdery_mildew,
                       leaf_rust=variety_item.leaf_rust,
                       leaf_blight=variety_item.leaf_blight,
                       stripe_rust=variety_item.stripe_rust,
                       spinal_rust=variety_item.spinal_rust,
                       smut=variety_item.smut)
    if form.validate_on_submit():
        variety_item.update(**form.data)
        flash(f'Information of Variety {variety_item.variety_name} Updated.',
              'success')
        return redirect(url_for('auth.tasks'))
    return render_template('variety/variety_edit.html',
                           form=form,
                           create=False,
                           variety_id=variety_id)


@variety.route('/del/<variety_id>/', methods=['GET'])
@login_required
def remove(variety_id):
    variety_item = VarietyDetail.query.get(variety_id)
    if current_user.id != variety_item.provider:
        flash('Not authorized!', 'warning')
        return redirect(url_for('auth.account'))    
    variety_item.delete()
    return redirect(url_for('auth.tasks'))

