# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
home_ad_blue = Blueprint('home_ad', __name__, template_folder='../../templates',
                         static_folder='../../statices', url_prefix='/home_ad')


@home_ad_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('home_ad/list.html')


@home_ad_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('home_ad/add.html')


@home_ad_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('home_ad/edit.html', _id=_id)
