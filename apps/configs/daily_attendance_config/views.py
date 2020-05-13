# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check

daily_attendance_config_blue = Blueprint('daily_attendance_config', __name__,
                                         template_folder='/templates',
                                         static_folder='../../../statices',
                                         url_prefix='/daily_attendance_config')


@daily_attendance_config_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('daily_attendance_config/list.html')


@daily_attendance_config_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('daily_attendance_config/add.html')


@daily_attendance_config_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('daily_attendance_config/edit.html', _id=_id)
