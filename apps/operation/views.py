# -*- coding: utf8 -*-


from flask import Blueprint, render_template

from libs.common import login_check

operation_blue = Blueprint('operation', __name__, template_folder='../../templates', static_folder='../../statices',
                        url_prefix='/operation')


@operation_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    return render_template('operation/ope_set.html')
