# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
product_blue = Blueprint('product', __name__, template_folder='../../templates',
                            static_folder='../../statices', url_prefix='/product')


@product_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('product/list.html')


@product_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('product/add.html')


@product_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('product/edit.html', _id=_id)
