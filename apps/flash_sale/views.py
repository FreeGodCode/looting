# -*- coding: utf8 -*-
from datetime import datetime, timedelta

from bson import ObjectId
from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt
from libs.db import flash_sale_template

crypt_obj = XKcrypt()
flash_sale_blue = Blueprint('flash_sale', __name__, template_folder='../../templates',
                            static_folder='../../statices', url_prefix='/flash_sale')


@flash_sale_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('flash_sale/list.html')


@flash_sale_blue.route('/add', methods=['get'])
@login_check
def add():
    now = datetime.now()
    date_list = []
    for i in range(30):
        temp = (now + timedelta(days=i)).strftime('%Y/%m/%d')
        date_list.append(temp)
    hour_list = []
    for i in range(24):
        hour_list.append(i)
    return render_template('flash_sale/add.html', date_list=date_list, hour_list=hour_list)


@flash_sale_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    now = datetime.now()
    date_list = []
    for i in range(30):
        temp = (now + timedelta(days=i)).strftime('%Y/%m/%d')
        date_list.append(temp)
    hour_list = []
    for i in range(24):
        hour_list.append(i)
    return render_template('flash_sale/edit.html', _id=_id, date_list=date_list, hour_list=hour_list)


@flash_sale_blue.route('/real_list', methods=['get'])
@login_check
def real_list():
    return render_template('flash_sale/real_list.html')


@flash_sale_blue.route('/config', methods=['get'])
@login_check
def config():
    hour_list = []
    for i in range(24):
        hour_list.append(i)
    return render_template('flash_sale/config.html', hour_list=hour_list)
