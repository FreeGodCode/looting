# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check

withdraw_blue = Blueprint('withdraw', __name__, template_folder='../../templates',
                          static_folder='../../statices', url_prefix='/withdraw')


@withdraw_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('withdraw/list.html')

@withdraw_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('withdraw/edit.html', _id=_id)
