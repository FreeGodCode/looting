# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.crypt import XKcrypt

crypt_obj = XKcrypt()
task_event_blue = Blueprint('task_event', __name__, template_folder='../../templates',
                       static_folder='../../statices', url_prefix='/task_event')


@task_event_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('event/list.html')
