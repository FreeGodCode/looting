# -*- coding: utf8 -*-
from bson import ObjectId
from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.db import heat_task

heat_task_blue = Blueprint('heat_task', __name__, template_folder='../../templates',
                           static_folder='../../statices',
                           url_prefix='/heat_task')


@heat_task_blue.route('/list', methods=['GET'])
@login_check
def _list():
    return render_template('heat_task/list.html')


@heat_task_blue.route('/add', methods=['GET'])
@login_check
def add():
    return render_template('heat_task/add.html')


@heat_task_blue.route('/edit', methods=['GET'])
@login_check
def edit():
    _id = request.args.get('_id', '')
    if not _id or not ObjectId.is_valid(_id):
        return '404'
    _obj = heat_task.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return '404'
    del _obj['_id']
    return render_template('heat_task/edit.html', _id=_id, _obj=_obj)
