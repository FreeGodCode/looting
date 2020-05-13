# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check

invite_reward_config_blue = Blueprint('invite_reward_config', __name__,
                                      template_folder='/templates',
                                      static_folder='../../../statices',
                                      url_prefix='/invite_reward_config')


@invite_reward_config_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('invite_reward_config/list.html')


@invite_reward_config_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('invite_reward_config/add.html')


@invite_reward_config_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id')
    return render_template('invite_reward_config/edit.html', _id=_id)
