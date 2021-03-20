# -*- coding: utf8 -*-
# import sys

from bson import ObjectId
from flask import Blueprint, jsonify

from libs.common import get_request_params
from libs.crypt import XKcrypt
from libs.db import order
from libs.flask_ex import get_request_page_params, format_request_params, mg_regex_processor, int_keys_processor, \
    Resp, request_args_verify
from libs.permission import permissions_check
from libs.pymongo_ex import get_pageable
from model import (default_values, int_keys, order_info_processor, get_order_info)

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

order_api_blue = Blueprint('order_api', __name__, url_prefix='/api/order')


@order_api_blue.route('/my_list', methods=['get'])
@permissions_check('order:get', False)
def my_list():
    data = get_request_params()
    criteria = format_request_params(data, default_values,
                                     int_keys_processor(int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params(params=data)
    _cur = order.find(criteria)
    page_obj = get_pageable(_cur, page_num, limit, processor=order_info_processor)
    return Resp.ok(page_obj)


@order_api_blue.route('/detail', methods=['get'])
@permissions_check('order:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_order_info(_id)
    return jsonify({'code': 200, 'data': detail_obj})


@order_api_blue.route('/update', methods=['post'])
@permissions_check('order:edit', False)
def update():
    data = get_request_params()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _update = dict()
    _obj = order.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    for key in default_values:
        if key in data:
            _values = data.get(key)
            if _values:
                # if isinstance(_values, str) or isinstance(_values, unicode):
                if isinstance(_values, str):
                    _values = _values.strip()
                if key in int_keys:
                    try:
                        _values = int(_values)
                    except:
                        return jsonify({'code': 201, 'msg': u'参数错误'})
                    if _obj.get(key, None) != _values:
                        _update.update({key: _values})
    result = order.update_one({'_id': ObjectId(_id)}, {'$set': data})
    if result.matched_count:
        if result.modified_count:
            return jsonify({'code': 200, 'msg': u'成功'})
        else:
            return jsonify({'code': 204, 'msg': u'更新失败'})
    return jsonify({'code': 202, 'msg': u'不存在'})


@order_api_blue.route('/sent', methods=['post'])
@permissions_check('order:edit', False)
@request_args_verify("<ObjectId:_id>", "<str:waybill_num>", ObjectIds=['_id'])
def order_sent(_id, waybill_num):
    order.update_one({'_id': _id}, {'$set': {'waybill_num': waybill_num, 'status': 1}})
    return Resp.ok()
