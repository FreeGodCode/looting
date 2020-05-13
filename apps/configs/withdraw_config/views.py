# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check

withdraw_config_blue = Blueprint('withdraw_config', __name__,
                                 template_folder='/templates',
                                 static_folder='../../../statices',
                                 url_prefix='/withdraw_config')


@withdraw_config_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('withdraw_config/list.html')


@withdraw_config_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('withdraw_config/add.html')


@withdraw_config_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('withdraw_config/edit.html', _id=_id)


@withdraw_config_blue.route('/class_add', methods=['get'])
@login_check
def class_add():
    return render_template('withdraw_config/class_add.html')


@withdraw_config_blue.route('/class_edit', methods=['get'])
@login_check
def class_edit():
    _id = request.args.get('_id')
    return render_template('withdraw_config/class_edit.html', _id=_id)
