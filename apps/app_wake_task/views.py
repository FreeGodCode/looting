# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
app_wake_task_blue = Blueprint('app_wake_task', __name__, template_folder='../../templates',
                               static_folder='../../statices', url_prefix='/app_wake_task')


@app_wake_task_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('app_wake_task/list.html')


@app_wake_task_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('app_wake_task/add.html')


@app_wake_task_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('app_wake_task/edit.html', _id=_id)
