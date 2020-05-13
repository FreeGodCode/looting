# -*- coding: utf8 -*-
from bson import ObjectId
from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.db import domain_h5

domain_h5_blue = Blueprint('domain_h5', __name__, template_folder='../../templates',
                           static_folder='../../statices',
                           url_prefix='/domain_h5')


@domain_h5_blue.route('/list', methods=['GET'])
@login_check
def _list():
    return render_template('domain_h5/list.html')


@domain_h5_blue.route('/add', methods=['GET'])
@login_check
def add():
    return render_template('domain_h5/add.html')


@domain_h5_blue.route('/edit', methods=['GET'])
@login_check
def edit():
    _id = request.args.get('_id', '')
    if not _id or not ObjectId.is_valid(_id):
        return '404'
    _obj = domain_h5.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return '404'
    del _obj['_id']
    return render_template('domain_h5/edit.html', _id=_id, _obj=_obj)
