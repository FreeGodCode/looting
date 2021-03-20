# -*- coding: utf8 -*-
# import sys
import time

from bson import ObjectId
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from libs.common import login_api_check, judging_permissions
from libs.db import (admin_user, login_log, income)
from libs.utils import timestamp_to_strftime
from model import (default_values, int_key, _insert)

# reload(sys)
# sys.setdefaultencoding('utf-8')

income_api_blue = Blueprint('income_api', __name__, url_prefix='/api/income')


@income_api_blue.route('/my_list', methods=['get'])
@login_api_check()
def my_list():
    criteria = {}
    # 支持表格字段里的任何搜索
    access_status = judging_permissions('2_1_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    for item in default_values:
        req_value = request.args.get(item)
        if req_value:
            req_value = req_value.strip()
            if item in int_key:
                try:
                    req_value = int(req_value)
                except:
                    return jsonify({'code': 201, 'msg': u'参数错误'})
                criteria.update({item: req_value})
            else:
                criteria.update({item: {'$regex': req_value}})

    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = income.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('_id', -1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                _list.append(_obj)
            except Exception as e:
                print (e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@income_api_blue.route('/add', methods=['POST'])
@login_api_check()
def add():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    access_status = judging_permissions('2_1_0')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    created_time = timestamp_to_strftime(time.time() + 24 * 60 * 60, format='%Y-%m-%d')
    income_obj = income.find_one({'created_time': created_time})
    if income_obj:
        return jsonify({'code': 202, 'msg': u'当天收益已存在请不要重复添加'})
    income_obj = income.find_one({'created_time': timestamp_to_strftime(time.time(), format='%Y-%m-%d')})
    if income_obj:
        data['historical_income'] = int(data.get('yesterday_income', 0)) + income_obj.get('historical_income')
    else:
        data['historical_income'] = data.get('yesterday_income', 0)

    result = _insert(data)
    if result.get('status', False):
        return jsonify({'code': 200, 'msg': u'成功'})
    else:
        return jsonify({'code': 203, 'msg': result.get('msg', '')})


@income_api_blue.route('/detail', methods=['get'])
@login_api_check()
def detail():
    access_status = judging_permissions('2_1_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _id = request.args.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = income.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})

    _obj['_id'] = _id
    return jsonify({'code': 200, 'data': _obj})


@income_api_blue.route('/update', methods=['post'])
@login_api_check()
def update():
    access_status = judging_permissions('2_1_2')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _update = {}
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = income.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    for key in default_values:
        if key in data:
            _values = data.get(key)
            if _values:
                # if isinstance(_values, str) or isinstance(_values, unicode):
                if isinstance(_values, str):
                    _values = _values.strip()
                if key in int_key:
                    try:
                        _values = int(_values)
                    except:
                        return jsonify({'code': 201, 'msg': u'参数错误'})
                if _obj.get(key) != _values:
                    if key == 'password':
                        _values = generate_password_hash(_values)
                    _update.update({key: _values})
    if _update:
        try:
            income.update_one({'_id': ObjectId(_id)}, {'$set': _update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})


@income_api_blue.route('/delete', methods=['delete', 'post'])
@login_api_check()
def delete():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    access_status = judging_permissions('2_1_1')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    income.remove({'_id': ObjectId(_id)})
    return jsonify({'code': 200, 'msg': u'成功'})
