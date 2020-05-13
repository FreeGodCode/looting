# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
redbag_game_blue = Blueprint('redbag_game', __name__, template_folder='../../templates',
                             static_folder='../../statices', url_prefix='/redbag_game')


@redbag_game_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('redbag_game/list.html')


@redbag_game_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('redbag_game/add.html')


@redbag_game_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('redbag_game/edit.html', _id=_id)
