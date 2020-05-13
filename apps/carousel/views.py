# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
carousel_blue = Blueprint('carousel', __name__, template_folder='../../templates',
                          static_folder='../../statices', url_prefix='/carousel')


@carousel_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('carousel/list.html')


@carousel_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('carousel/add.html')


@carousel_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('carousel/edit.html', _id=_id)
