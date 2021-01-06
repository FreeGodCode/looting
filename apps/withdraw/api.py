# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from libs.common import get_request_params, get_current_real_name
from libs.flask_ex import format_request_params, mg_regex_processor, int_keys_processor, get_request_page_params, Resp, \
    request_args_verify
from libs.permission import permissions_check
from model import (default_values, int_keys, get_withdraw_order_list, get_withdraw_order_detail, set_audit_success,
                   set_audit_fail)

# reload(sys)
# sys.setdefaultencoding('utf-8')

withdraw_api_blue = Blueprint('withdraw_api', __name__, url_prefix='/api/withdraw')


@withdraw_api_blue.route('/my_list', methods=['get'])
@permissions_check('withdraw:get')
def my_list():
    criteria = format_request_params(get_request_params(),
                                     default_values,
                                     int_keys_processor(int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()
    page_obj = get_withdraw_order_list(criteria, page_num, limit)
    return Resp.ok(page_obj)


@withdraw_api_blue.route('/detail', methods=['get'])
@permissions_check('withdraw:get')
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_withdraw_order_detail(_id)
    return Resp.ok(detail_obj)


@withdraw_api_blue.route('/update', methods=['post'])
@permissions_check('withdraw:edit')
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def update(_id):
    return Resp.ok()


@withdraw_api_blue.route('/success', methods=['put'])
@permissions_check('withdraw:edit')
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def audit_success(_id):
    auditor_name = get_current_real_name()
    set_audit_success(auditor_name, _id)
    return Resp.ok()


@withdraw_api_blue.route('/success', methods=['put'])
@permissions_check('withdraw:edit')
@request_args_verify("<ObjectId:_id>", 'fail_msg', ObjectIds=['_id'])
def audit_fail(_id, fail_msg):
    auditor_name = get_current_real_name()
    set_audit_fail(auditor_name, _id, fail_msg)
    return Resp.ok()


if __name__ == '__main__':
    pass
