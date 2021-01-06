# -*- coding: utf8 -*-
import sys

from bson import ObjectId
from flask import Blueprint, request, jsonify

from conf import conf
from libs.common import (login_api_check, judging_permissions, get_request_params)
from libs.crypt import XKcrypt
from libs.db import user, invite_code_data, earth_code
from libs.flask_ex import format_request_params, mg_regex_processor, int_keys_processor, get_request_page_params, Resp
from libs.permission import permissions_check
from libs.pymongo_ex import get_pageable
from libs.utils import generate_dwz
from model import (default_values, int_keys, status_values, sex_values,
                   verified_status_values)

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

user_api_blue = Blueprint('user_api', __name__, url_prefix='/api/user')


@user_api_blue.route('/my_list', methods=['get'])
@permissions_check('user:get')
def my_list():
    criteria = {}
    criteria = format_request_params(get_request_params(),
                                     default_values,
                                     int_keys_processor(int_keys),
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()
    _cur = user.find(criteria)
    page_obj = get_pageable(_cur, page_num, limit)
    return Resp.ok(page_obj)


@user_api_blue.route('/edit', methods=['get'])
@login_api_check()
def edit():
    _id = request.args.get('_id')
    if not _id:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = user.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    access_status = judging_permissions('1_0_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _obj['_id'] = _id
    _obj['status_name'] = status_values.get(_obj.get('status', 0))
    _obj['sex_name'] = sex_values.get(_obj.get('sex', 0))
    _obj['new_value_name'] = new_value_values.get(_obj.get('new_value'))
    _obj['grade_name'] = grade_values.get(_obj.get('grade', 1))
    _obj['verified_status_name'] = verified_status_values.get(_obj.get('verified_status'))
    return jsonify({'code': 200, 'data': _obj})


@user_api_blue.route('/update', methods=['post'])
@login_api_check(True)
def update():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')

    if not _id:
        return jsonify({'code': 201, 'msg': u'缺少参数'})
    _obj = user.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    invite_code = data.get('invite_code', '').lower()
    data.update({'invite_code': invite_code})
    access_status = judging_permissions('1_0_2')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _update = {}

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
                if _obj.get(key) != _values:
                    _update.update({key: _values})
    new_update = {}
    if 'status' in _update:
        new_update['status'] = _update.get('status')
    if 'verified_status' in _update:
        new_update['verified_status'] = _update.get('verified_status')
    if 'invite_code' in _update:
        invite_code = _update.get('invite_code')
        invite_code_obj = invite_code_data.find_one({'invite_code': invite_code})
        user_obj = user.find_one({'invite_code': invite_code})
        earth_code_obj = earth_code.find_one({'invite_code': invite_code})
        if invite_code_obj or user_obj or earth_code_obj:
            return jsonify({'code': 201, 'msg': u'邀请码已被使用'})
        invite_url_short = generate_dwz(
            '{0}/h5/reg?invite_code={1}&source=invite'.format(conf.api_url, invite_code))
        new_update['invite_code'] = invite_code
        new_update['invite_url_short'] = invite_url_short
    if new_update:
        try:

            user.update_one({'_id': ObjectId(_id)}, {'$set': new_update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})
