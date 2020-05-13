# -*- coding: utf8 -*-
import json
import sys

from flask import Blueprint, jsonify, request

from libs.common import login_api_check, judging_permissions
from libs.db import operation
from model import (default_values, int_key, float_key, _insert)

reload(sys)
sys.setdefaultencoding("utf-8")

operation_api_blue = Blueprint('operation_api', __name__, url_prefix='/api/operation')


@operation_api_blue.route('/detail', methods=['get'])
@login_api_check()
def detail():
    access_status = judging_permissions('operation:get')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _obj = operation.find_one({})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})

    _obj['_id'] = str(_obj['_id'])
    return jsonify({'code': 200, 'data': _obj})


@operation_api_blue.route('/update', methods=['post'])
@login_api_check(True)
def update():
    access_status = judging_permissions('operation:edit')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _update = {}
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _obj = operation.find_one()
    if not _obj:
        result = _insert(data)
        if result.get('status'):
            return jsonify({'code': 200, 'msg': u'成功'})
        return jsonify({'code': 200, 'msg': u'不存在'})


    try:
        red_hour_per_json = json.loads(data.get('red_hour_per_json'))
    except:
        return jsonify({'code': 201, 'msg': u'红包时间点分配比例json数据错误'})
    per_total = 0
    for hour_int in range(24):
        hour_dict = red_hour_per_json.get(str(hour_int))
        if not hour_dict:
            return jsonify({'code': 201, 'msg': u'红包时间点分配比例json数据错误'})
        per_total += hour_dict.get('per', 0)
    if per_total != 100:
        return jsonify({'code': 201, 'msg': u'红包时间点分配比例json数据错误'})
    red_hour_per_json_str = json.dumps(red_hour_per_json, ensure_ascii=False)
    data.update({'red_hour_per_json': red_hour_per_json_str})


    try:
        check_in_calorific_json = json.loads(data.get('check_in_calorific_json'))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    check_in_calorific_json_str = json.dumps(check_in_calorific_json, ensure_ascii=False)
    data.update({'check_in_calorific_json': check_in_calorific_json_str})

    try:
        calorific_cash_json = json.loads(data.get('calorific_cash_json'))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    calorific_cash_json_str = json.dumps(calorific_cash_json, ensure_ascii=False)
    data.update({'calorific_cash_json': calorific_cash_json_str})

    try:
        withdraw_cash_json = json.loads(data.get('withdraw_cash_json'))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    withdraw_cash_json_str = json.dumps(withdraw_cash_json, ensure_ascii=False)
    data.update({'withdraw_cash_json': withdraw_cash_json_str})

    try:
        withdraw_cash_json_new = json.loads(data.get('withdraw_cash_json_new'))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    withdraw_cash_json_new_str = json.dumps(withdraw_cash_json_new, ensure_ascii=False)
    data.update({'withdraw_cash_json_new': withdraw_cash_json_new_str})

    for key in default_values:

        if key in data:
            _values = data.get(key)
            if isinstance(_values, str) or isinstance(_values, unicode):
                _values = _values.strip()
            if key in int_key:
                try:
                    _values = int(_values)
                except:
                    return jsonify({'code': 201, 'msg': u'参数错误'})
            if key in float_key:
                try:
                    _values = float(_values)
                except:
                    return jsonify({'code': 201, 'msg': u'参数错误'})
            if _obj.get(key) != _values:
                _update.update({key: _values})

    if _update:
        try:
            operation.update_one({'_id': _obj.get('_id')}, {'$set': _update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})
