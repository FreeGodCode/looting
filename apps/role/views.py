# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request, Markup

from apps.login.model import admin_navs
from libs.common import login_check
from libs.crypt import XKcrypt
from libs.db import role_authority

crypt_obj = XKcrypt()
role_blue = Blueprint('role', __name__, template_folder='../../templates',
                      static_folder='../../statices', url_prefix='/role')


@role_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('role/list.html')


@role_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('role/add.html')


@role_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('role/edit.html', _id=_id)


@role_blue.route('/authority', methods=['get'])
@login_check
def authority():
    _id = request.args.get('_id')
    ole_authority_cur = role_authority.find({'role_id': _id}).sort([('authority', 1)])
    ole_authority_id_list = []
    for ole_authority_obj in ole_authority_cur:
        ole_authority_id_list.append(ole_authority_obj.get('authority'))
    authority_html_list = []
    for itme in admin_navs[1: -1]:
        authority_html_list.append('<div class="layui-form-item">')
        authority_html_list.append('<blockquote class="layui-elem-quote">{0}</blockquote>'.format(itme.get('title')))
        authority_html_list.append('</div>')
        for children in itme.get('children'):
            authority_html_list.append('<div class="layui-form-item">')
            authority_html_list.append('<label class="layui-form-label">{0}</label>'.format(children.get('title')))
            authority_html_list.append('<div class="layui-input-block">')
            authority_list = children.get('authority_list')
            try:
                for authority_obj in authority_list:
                    title = authority_obj.get('title')
                    name = str(authority_obj.get('value'))
                    if role_authority.find_one({'role_id': _id, 'authority': name}):
                        authority_html_list.append(
                            '<input type="checkbox" name="{0}" title="{1}" checked>'.format(name, title))
                    else:
                        authority_html_list.append('<input type="checkbox" name="{0}" title="{1}">'.format(name, title))
            except:
                pass
            authority_html_list.append('</div></div>')
    return render_template('role/allot_authority.html', _id=_id, authority_html=Markup(''.join(authority_html_list)))
