# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
daily_task_blue = Blueprint('daily_task', __name__, template_folder='../../templates',
                            static_folder='../../statices', url_prefix='/daily_task')


@daily_task_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('daily_task/list.html')


@daily_task_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('daily_task/add.html')


@daily_task_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('daily_task/edit.html', _id=_id)
