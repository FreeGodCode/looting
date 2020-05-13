# -*- coding: utf8 -*-
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
daily_new_blue = Blueprint('daily_new', __name__, template_folder='../../templates',
                           static_folder='../../statices', url_prefix='/daily_new')


@daily_new_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('daily_new/list.html')


@daily_new_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('daily_new/add.html')


@daily_new_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('daily_new/edit.html', _id=_id)


@daily_new_blue.route('/real_list', methods=['get'])
@login_check
def real_list():
    return render_template('daily_new/real_list.html')
