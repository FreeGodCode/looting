# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
version_manag_blue = Blueprint('version_manag', __name__, template_folder='../../templates',
                               static_folder='../../statices', url_prefix='/version_manag')


@version_manag_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('version_manag/list.html')


@version_manag_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('version_manag/add.html')


@version_manag_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('version_manag/edit.html', _id=_id)
