# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check

dividend_config_blue = Blueprint('dividend_config', __name__,
                                 template_folder='/templates',
                                 static_folder='../../../statices',
                                 url_prefix='/dividend_config')


@dividend_config_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('dividend_config/list.html')


@dividend_config_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('dividend_config/add.html')


@dividend_config_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('dividend_config/edit.html', _id=_id)
