# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check

daily_new_config_blue = Blueprint('daily_new_config', __name__,
                                  template_folder='/templates',
                                  static_folder='../../../statices',
                                  url_prefix='/daily_new_config')


@daily_new_config_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('daily_new_config/list.html')


@daily_new_config_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('daily_new_config/add.html')


@daily_new_config_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('daily_new_config/edit.html', _id=_id)
