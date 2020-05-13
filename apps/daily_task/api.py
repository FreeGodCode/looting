# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from apps.daily_task.model import model, get_list_obj, update_obj, delete_obj, create_obj, get_detail_obj, \
    get_top_task_detail, update_top_task
from libs.common import get_request_params
from libs.crypt import XKcrypt
from libs.flask_ex import Resp, request_args_verify, format_request_params, mg_regex_processor, int_keys_processor, \
    get_request_page_params
from libs.permission import permissions_check

crypt_obj = XKcrypt()

reload(sys)
sys.setdefaultencoding('utf-8')

daily_task_api_blue = Blueprint('daily_task_api', __name__, url_prefix='/api/daily_task')


@daily_task_api_blue.route('/my_list', methods=['get'])
@permissions_check('daily_task:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     [
                                         int_keys_processor(model.int_keys)
                                     ],
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()
    page_obj = get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@daily_task_api_blue.route('/add', methods=['POST'])
@permissions_check('daily_task:add', False)
def add():
    data = get_request_params()
    daily_new_data = format_request_params(data,
                                           model.default_values,
                                           [
                                               int_keys_processor(model.int_keys)
                                           ],
                                           convert_object_id=True,
                                           full_fields=True)
    create_obj(daily_new_data)
    return Resp.ok()


@daily_task_api_blue.route('/detail', methods=['get'])
@permissions_check('daily_task:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_detail_obj(_id)
    return Resp.ok(detail_obj)


@daily_task_api_blue.route('/update', methods=['post'])
@permissions_check('daily_task:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_data = format_request_params(get_request_params(),
                                        model.default_values,
                                        [
                                            int_keys_processor(model.int_keys)
                                        ],
                                        convert_object_id=True)
    update_obj(_id, update_data)
    return Resp.ok()


@daily_task_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('daily_task:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    delete_obj(_id)
    return Resp.ok()


@daily_task_api_blue.route('/top_update', methods=['post'])
@permissions_check('daily_task:edit', False)
def top_update():
    update_data = format_request_params(get_request_params(),
                                        model.top_default_values,
                                        [
                                            int_keys_processor(model.top_int_keys)
                                        ],
                                        convert_object_id=True)
    update_top_task(update_data)
    return Resp.ok()


@daily_task_api_blue.route('/top_detail', methods=['get'])
@permissions_check('daily_task:get', False)
def top_detail():
    detail_obj = get_top_task_detail()
    return Resp.ok(detail_obj)
