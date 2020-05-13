# -*- coding: utf8 -*-

from flask import Blueprint, render_template

from libs.common import login_check

invite_task_config_blue = Blueprint('invite_task_config', __name__,
                                    template_folder='/templates',
                                    static_folder='../../../statices',
                                    url_prefix='/invite_task_config')


@invite_task_config_blue.route('/edit', methods=['get'])
@login_check
def edit():
    return render_template('invite_task_config/edit.html')
