# -*- coding: utf8 -*-
from flask import Blueprint, render_template, request

from libs.common import login_check

leaderboard_withdraw_blue = Blueprint('leaderboard_withdraw', __name__, template_folder='../../templates',
                                      static_folder='../../statices',
                                      url_prefix='/leaderboard_withdraw')


@leaderboard_withdraw_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('leaderboard_withdraw/list.html')


@leaderboard_withdraw_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('leaderboard_withdraw/add.html')


@leaderboard_withdraw_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id', '')
    if not _id:
        return '404'
    return render_template('leaderboard_withdraw/edit.html', _id=_id)
