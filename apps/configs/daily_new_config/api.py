# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from libs.common import get_request_params
from libs.flask_ex import get_request_page_params, format_request_params, request_args_verify, mg_regex_processor, \
    int_keys_processor, Resp
from libs.permission import permissions_check
from .model import model

reload(sys)
sys.setdefaultencoding('utf-8')

daily_new_config_api_blue = Blueprint('daily_new_config_api', __name__, url_prefix='/api/daily_new_config')


@daily_new_config_api_blue.route('/my_list', methods=['get'])
@permissions_check('daily_new_config:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     [
                                         int_keys_processor(model.int_keys)
                                     ],
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()
    page_obj = model.get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@daily_new_config_api_blue.route('/add', methods=['POST'])
@permissions_check('daily_new_config:add', False)
def add():
    data = get_request_params()
    daily_new_data = format_request_params(data,
                                           model.default_values,
                                           [
                                               int_keys_processor(model.int_keys)
                                           ],
                                           convert_object_id=True,
                                           full_fields=True)
    model.create_obj(daily_new_data)
    return Resp.ok()


@daily_new_config_api_blue.route('/detail', methods=['get'])
@permissions_check('daily_new_config:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = model.get_detail_obj(_id)
    return Resp.ok(detail_obj)


@daily_new_config_api_blue.route('/update', methods=['post'])
@permissions_check('daily_new_config:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_data = format_request_params(get_request_params(),
                                        model.default_values,
                                        [
                                            int_keys_processor(model.int_keys)
                                        ],
                                        convert_object_id=True)
    model.update_obj(_id, update_data)
    return Resp.ok()


@daily_new_config_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('daily_new_config:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    model.remove_obj(_id)
    return Resp.ok()
