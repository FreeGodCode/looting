# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request, Markup

from libs.common import login_check
from libs.crypt import XKcrypt
from libs.db import user_role, role

crypt_obj = XKcrypt()
admin_blue = Blueprint('admin', __name__, template_folder='../../templates',
                       static_folder='../../statices', url_prefix='/admin')


@admin_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('admin/list.html')


@admin_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('admin/add.html')


@admin_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id', '')
    if not _id:
        return '404'
    return render_template('admin/edit.html', _id=_id)


@admin_blue.route('/role', methods=['get'])
@login_check
def allot_role():
    _id = request.args.get('_id', '')
    if not _id:
        return '404'
    role_cur = role.find({})
    checkbox_list = []
    for role_obj in role_cur:
        name = role_obj.get('name')
        role_id = str(role_obj.get('_id'))
        if user_role.find_one({'role_id': role_id, 'user_id': _id}):
            checkbox_list.append('<input type="checkbox" name="{0}" title="{1}" checked>'.format(role_id, name))
        else:
            checkbox_list.append('<input type="checkbox" name="{0}" title="{1}">'.format(role_id, name))
    checkbox_html = '\n'.join(checkbox_list)
    return render_template('admin/allot_role.html', _id=_id, checkbox_html=Markup(checkbox_html))
