# -*- coding: utf8 -*-
from flask import Blueprint, render_template, request

from libs.common import login_check

integer_red_blue = Blueprint('integer_red', __name__, template_folder='../../templates',
                             static_folder='../../statices',
                             url_prefix='/integer_red')


@integer_red_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('integer_red/list.html')


@integer_red_blue.route('/detail_list', methods=['get'])
@login_check
def detail_list():
    integer_red_id = request.args.get('integer_red_id', '')
    return render_template('integer_red/detail_list.html', integer_red_id=integer_red_id)

