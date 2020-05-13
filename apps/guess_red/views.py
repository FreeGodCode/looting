# -*- coding: utf8 -*-
from flask import Blueprint, render_template, request

from libs.common import login_check

guess_red_blue = Blueprint('guess_red', __name__, template_folder='../../templates',
                           static_folder='../../statices',
                           url_prefix='/guess_red')


@guess_red_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('guess_red/list.html')


@guess_red_blue.route('/detail_list', methods=['get'])
@login_check
def detail_list():
    guess_red_id = request.args.get('guess_red_id', '')
    return render_template('guess_red/detail_list.html', guess_red_id=guess_red_id)
