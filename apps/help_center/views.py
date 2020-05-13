# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
help_center_blue = Blueprint('help_center', __name__, template_folder='../../templates',
                             static_folder='../../statices', url_prefix='/help_center')


@help_center_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('help_center/list.html')


@help_center_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('help_center/add.html')


@help_center_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('help_center/edit.html', _id=_id)
