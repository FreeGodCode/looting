# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from libs.common import get_request_params
from libs.flask_ex import get_request_page_params, format_request_params, request_args_verify, mg_regex_processor, \
    int_keys_processor, Resp
from libs.permission import permissions_check
from model import model

reload(sys)
sys.setdefaultencoding('utf-8')

daily_attendance_config_api_blue = Blueprint('daily_attendance_config_api', __name__,
                                             url_prefix='/api/daily_attendance_config')


def daily_attendance_info_processor(obj):
    return obj


@daily_attendance_config_api_blue.route('/my_list', methods=['get'])
@permissions_check('daily_attendance:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()

    page_obj = model.get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@daily_attendance_config_api_blue.route('/detail', methods=['get'])
@permissions_check('daily_attendance:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = model.get_detail_obj(_id)
    return Resp.ok(detail_obj)


@daily_attendance_config_api_blue.route('/add', methods=['post'])
@permissions_check('daily_attendance:add', False)
def add():
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys),
                                        full_fields=True)
    model.create_obj(update_dict)
    return Resp.ok()


@daily_attendance_config_api_blue.route('/update', methods=['post'])
@permissions_check('daily_attendance:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys)
                                        )

    model.update_obj(_id, update_dict)
    return Resp.ok()


@daily_attendance_config_api_blue.route('/delete', methods=['delete'])
@permissions_check('daily_attendance:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    model.remove_obj(_id)
    return Resp.ok()
