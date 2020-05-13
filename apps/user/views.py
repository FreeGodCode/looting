# -*- coding: utf8 -*-

from bson import ObjectId
from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.db import user

user_blue = Blueprint('user', __name__, template_folder='../../templates', static_folder='../../statices',
                      url_prefix='/user')


@user_blue.route('/list', methods=['get'])
@login_check
def _list():
    user_id = request.args.get('user_id', '')
    invite_id = request.args.get('invite_id', '')
    return render_template('user/list.html', user_id=user_id, invite_id=invite_id)


@user_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('user/add.html')


@user_blue.route('/show_audit_failure', methods=['get'])
@login_check
def show_audit_failure():
    _id = request.args.get('_id', '')
    if not _id:
        return '404'
    return render_template('user/show_audit_failure.html', _id=_id)


@user_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id', '')
    if not _id:
        return '404'
    user_obj = user.find_one({'_id': ObjectId(_id)})
    if not user_obj:
        return '404'
    headimgurl = user_obj.get('headimgurl', '')
    return render_template('user/edit.html', _id=_id, headimgurl=headimgurl)
