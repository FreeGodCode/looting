# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from libs.common import get_request_params
from libs.crypt import XKcrypt
from libs.flask_ex import format_request_params, int_keys_processor, mg_regex_processor, get_request_page_params, \
    Resp, request_args_verify, map_processor, exists_processor
from libs.permission import permissions_check
from model import (model, get_list_obj, create_obj, update_obj, delete_obj, get_detail_obj, get_real_list_obj)

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

daily_new_api_blue = Blueprint('daily_new_api', __name__, url_prefix='/api/daily_new')


@daily_new_api_blue.route('/my_list', methods=['get'])
@permissions_check('daily_new:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()
    page_obj = get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@daily_new_api_blue.route('/add', methods=['POST'])
@permissions_check('daily_new:add', False)
@request_args_verify('<int:total_lottery_num>', '<int:lottery_cost_value>')
def add(total_lottery_num, lottery_cost_value):
    data = get_request_params()
    daily_new_data = format_request_params(data,
                                           model.default_values,
                                           [
                                               int_keys_processor(model.int_keys)

                                           ],
                                           convert_object_id=True,
                                           begin_processors=map_processor('(.+)\[(.+)\]'),
                                           full_fields=True)
    create_obj(daily_new_data, total_lottery_num, lottery_cost_value)
    return Resp.ok()


@daily_new_api_blue.route('/detail', methods=['get'])
@permissions_check('daily_new:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_detail_obj(_id)
    return Resp.ok(detail_obj)


@daily_new_api_blue.route('/update', methods=['post'])
@permissions_check('daily_new:edit', False)
@request_args_verify('<ObjectId:_id>',
                     '<int:total_lottery_num>',
                     '<int:lottery_cost_value>',
                     ObjectIds=['_id'])
def update(_id, total_lottery_num, lottery_cost_value):
    update_data = format_request_params(get_request_params(),
                                        model.default_values,
                                        [
                                            int_keys_processor(model.int_keys)
                                        ],
                                        convert_object_id=True,
                                        begin_processors=[
                                            map_processor('(.+)\[(.+)\]'),
                                            exists_processor(['auto_result', 'auto_putaway'], [1, 0])
                                        ])
    update_obj(_id, update_data, total_lottery_num, lottery_cost_value)
    return Resp.ok()


@daily_new_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('daily_new:delete', False)
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def delete(_id):
    delete_obj(_id)
    return Resp.ok()


@daily_new_api_blue.route('/real_list', methods=['get'])
@permissions_check('daily_new:get', False)
def real_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()
    page_obj = get_real_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)
