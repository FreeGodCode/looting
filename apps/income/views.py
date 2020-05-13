# -*- coding: utf8 -*-

from flask import Blueprint, render_template, request

from libs.common import login_check

income_blue = Blueprint('income', __name__, template_folder='../../templates',
                        static_folder='../../statices', url_prefix='/income')


@income_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('income/list.html')


@income_blue.route('/add', methods=['get'])
@login_check
def add():
    return render_template('income/add.html')


@income_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    _id = request.args.get('_id')
    return render_template('income/edit.html', _id=_id)
