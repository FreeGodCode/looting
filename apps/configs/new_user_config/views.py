# -*- coding: utf8 -*-

from flask import Blueprint, render_template

from libs.common import login_check

new_user_config_blue = Blueprint('new_user_config', __name__,
                                 template_folder='/templates',
                                 static_folder='../../../statices',
                                 url_prefix='/new_user_config')


@new_user_config_blue.route('/edit', methods=['get'])
@login_check
def edit():
    return render_template('new_user_config/new_user_set.html')
