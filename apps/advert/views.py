# -*- coding: utf8 -*-
# from bson import ObjectId
from flask import Blueprint, render_template, request

from libs.common import login_check
# from libs.db import domain_h5
from libs.flask_ex import request_args_verify

advert_blue = Blueprint('advert', __name__, template_folder='../../templates',
                        static_folder='../../statices',
                        url_prefix='/advert')


@advert_blue.route('/list', methods=['GET'])
@login_check
def _list():
    return render_template('advert/list.html')


@advert_blue.route('/add', methods=['GET'])
@login_check
def add():
    return render_template('advert/add.html')


@advert_blue.route('/edit', methods=['GET'])
@login_check
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def edit(_id):
    return render_template('advert/edit.html', _id=_id)
