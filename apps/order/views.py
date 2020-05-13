# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
order_blue = Blueprint('order', __name__, template_folder='../../templates',
                       static_folder='../../statices', url_prefix='/order')


@order_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('order/list.html')


@order_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('order/edit.html', _id=_id)


@order_blue.route('/send', methods=['get'])
@login_check
def send():
    _id = request.args.get('_id')
    return render_template('order/send.html', _id=_id)
