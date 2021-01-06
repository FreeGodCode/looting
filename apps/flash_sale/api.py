# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from libs.common import get_request_params
from libs.crypt import XKcrypt
from libs.flask_ex import format_request_params, int_keys_processor, mg_regex_processor, get_request_page_params, \
    Resp, request_args_verify, list_processor, datetime_keys_processor
from libs.permission import permissions_check
from model import (model, update_obj, get_detail_obj,
                   create_obj, get_list_obj, delete_obj, get_real_list_obj, get_config_detail, update_config)

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

flash_sale_api_blue = Blueprint('flash_sale_api', __name__, url_prefix='/api/flash_sale')


@flash_sale_api_blue.route('/my_list', methods=['get'])
@permissions_check('flash_sale:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys),
                                     mg_regex_processor)

    page_num, limit = get_request_page_params()
    page_obj = get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@flash_sale_api_blue.route('/add', methods=['POST'])
@permissions_check('flash_sale:add', False)
@request_args_verify('<int:total_cost_num>', '<int:lottery_cost_value>')
def add(total_cost_num, lottery_cost_value):
    data = format_request_params(get_request_params(),
                                 model.default_values,
                                 [
                                     int_keys_processor(model.int_keys),
                                     datetime_keys_processor(['date_list'], '%Y/%m/%d')
                                 ],
                                 convert_object_id=True,
                                 begin_processors=list_processor(['date_list', 'hour_list']),
                                 full_fields=True)
    data['date_list'] = sorted(data['date_list'])
    data['hour_list'] = sorted(data['hour_list'])
    create_obj(data, total_cost_num, lottery_cost_value)
    return Resp.ok()


@flash_sale_api_blue.route('/detail', methods=['get'])
@permissions_check('flash_sale:get', False)
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_detail_obj(_id)
    return Resp.ok(detail_obj)


@flash_sale_api_blue.route('/update', methods=['post'])
@permissions_check('flash_sale:edit', False)
@request_args_verify("<ObjectId:_id>",
                     '<int:total_cost_num>',
                     '<int:lottery_cost_value>',
                     ObjectIds=['_id'])
def update(_id, total_cost_num, lottery_cost_value):
    update_data = format_request_params(get_request_params(),
                                        model.default_values,
                                        [
                                            int_keys_processor(model.int_keys),
                                            datetime_keys_processor(['date_list'], '%Y/%m/%d')
                                        ],
                                        convert_object_id=True,
                                        begin_processors=list_processor(['date_list', 'hour_list']))
    update_obj(_id, update_data, total_cost_num, lottery_cost_value)
    return Resp.ok()


@flash_sale_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('flash_sale:delete', False)
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def delete(_id):
    delete_obj(_id)
    return Resp.ok()


@flash_sale_api_blue.route('/real_list', methods=['get'])
@permissions_check('flash_sale:get', False)
def real_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys),
                                     mg_regex_processor)

    page_num, limit = get_request_page_params()
    page_obj = get_real_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@flash_sale_api_blue.route('/config/detail', methods=['get'])
@permissions_check('flash_sale:get', False)
def config_detail():
    detail_obj = get_config_detail()
    return Resp.ok(detail_obj)


@flash_sale_api_blue.route('/config/update', methods=['post'])
@permissions_check('flash_sale:edit', False)
def config_update():
    update_data = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys),
                                        convert_object_id=True,
                                        begin_processors=list_processor(['hour_list']))
    if update_data.has_key('hour_list'):
        update_data['hour_list'] = sorted(update_data['hour_list'])
    update_config(update_data)
    return Resp.ok()
