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

dividend_config_api_blue = Blueprint('dividend_config_api', __name__, url_prefix='/api/dividend_config')


@dividend_config_api_blue.route('/my_list', methods=['get'])
@permissions_check('dividend_config:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()

    page_obj = model.get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@dividend_config_api_blue.route('/add', methods=['post'])
@permissions_check('dividend_config:add', False)
def add():
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys),
                                        full_fields=True)
    model.create_obj(update_dict)
    return Resp.ok()


@dividend_config_api_blue.route('/detail', methods=['get'])
@permissions_check('dividend_config:get', False)
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def detail(_id):
    detail_obj = model.get_detail_obj(_id)
    return Resp.ok(detail_obj)


@dividend_config_api_blue.route('/update', methods=['post'])
@permissions_check('dividend_config:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys)
                                        )

    model.update_obj(_id, update_dict)
    return Resp.ok()


@dividend_config_api_blue.route('/delete', methods=['delete'])
@permissions_check('dividend_config:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    model.remove_obj(_id)
    return Resp.ok()
