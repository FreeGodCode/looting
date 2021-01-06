# -*- coding: utf8 -*-
# import sys

from flask import Blueprint, jsonify

from libs.common import get_request_params
from libs.db import configs, CONFIG_TYPE_APP_ROUTE
from libs.flask_ex import get_request_page_params, format_request_params, request_args_verify, mg_regex_processor, \
    int_keys_processor, Resp
from libs.permission import permissions_check
from model import model

# reload(sys)
# sys.setdefaultencoding('utf-8')

route_config_api_blue = Blueprint('route_config_api', __name__, url_prefix='/api/route_config')


def invite_reward_config_info_processor(obj):
    return obj


@route_config_api_blue.route('/my_list', methods=['get'])
@permissions_check('route_config:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()

    page_obj = model.get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@route_config_api_blue.route('/detail', methods=['get'])
@permissions_check('route_config:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = model.get_detail_obj(_id)
    return Resp.ok(detail_obj)


@route_config_api_blue.route('/add', methods=['post'])
@permissions_check('route_config:add', False)
def add():
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys),
                                        full_fields=True)
    model.create_obj(update_dict)
    return Resp.ok()


@route_config_api_blue.route('/update', methods=['post'])
@permissions_check('route_config:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    # 支持表格字段里的任何搜索
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys))
    configs.update_one({'_id': _id, 'type_num': CONFIG_TYPE_APP_ROUTE}, {'$set': update_dict})
    return jsonify({'code': 200, 'msg': u'success'})


@route_config_api_blue.route('/delete', methods=['post'])
@permissions_check('route_config:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    model.remove_obj(_id)
    return Resp.ok()
