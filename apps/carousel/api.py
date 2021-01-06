# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from libs.common import get_request_params
from libs.crypt import XKcrypt
from libs.flask_ex import format_request_params, int_keys_processor, get_request_page_params, Resp, request_args_verify
from libs.permission import permissions_check
from model import (model, get_list_obj, create_obj, get_detail_obj, delete_obj, update_obj)

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

carousel_api_blue = Blueprint('carousel_api', __name__, url_prefix='/api/carousel')


@carousel_api_blue.route('/my_list', methods=['get'])
@permissions_check('carousel:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys))
    page_num, limit = get_request_page_params()
    page_obj = get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@carousel_api_blue.route('/add', methods=['POST'])
@permissions_check('carousel:add', False)
def add():
    data = format_request_params(get_request_params(),
                                 model.default_values,
                                 int_keys_processor(model.int_keys),
                                 convert_object_id=True,
                                 full_fields=True)
    create_obj(data)
    return Resp.ok()


@carousel_api_blue.route('/detail', methods=['get'])
@permissions_check('carousel:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_detail_obj(_id)
    return Resp.ok(detail_obj)


@carousel_api_blue.route('/update', methods=['post'])
@permissions_check('carousel:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys),
                                        convert_object_id=True)
    update_obj(_id, update_dict)
    return Resp.ok()


@carousel_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('carousel:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    delete_obj(_id)
    return Resp.ok()
