# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
planet_img_blue = Blueprint('planet_img', __name__, template_folder='../../templates',
                            static_folder='../../statices', url_prefix='/planet_img')


@planet_img_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('planet_img/list.html')


@planet_img_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('planet_img/add.html')


@planet_img_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('planet_img/edit.html', _id=_id)
