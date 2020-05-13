# -*- coding: utf8 -*-
from flask import Blueprint, render_template, request

from libs.common import login_check

leaderboard_blue = Blueprint('leaderboard', __name__, template_folder='../../templates',
                             static_folder='../../statices',
                             url_prefix='/leaderboard')


@leaderboard_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('leaderboard/list.html')


@leaderboard_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('leaderboard/add.html')


@leaderboard_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id', '')
    if not _id:
        return '404'
    return render_template('leaderboard/edit.html', _id=_id)
