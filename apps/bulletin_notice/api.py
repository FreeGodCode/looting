# -*- coding: utf8 -*-
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify

from libs.common import login_api_check, judging_permissions, get_request_params
from libs.db import bulletin_notice
from model import default_values, _insert, int_key, status_values, type_num_values

bulletin_notice_api_blue = Blueprint('bulletin_notice_api', __name__, url_prefix='/api/bulletin_notice')


@bulletin_notice_api_blue.route('/my_list', methods=['GET'])
@login_api_check()
def _list():
    access_status = judging_permissions('2_1_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    criteria = {}
    # 支持表格字段里的任何搜索
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
    sort_list = [('type_num', 1), ('status', -1)]

    _cur = bulletin_notice.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []

        cur_list = _cur.sort(sort_list).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                _obj['status_name'] = status_values.get(_obj.get('status'))
                _obj['type_num_name'] = type_num_values.get(_obj.get('type_num'))
                _list.append(_obj)
            except Exception as e:
                print (e)

        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@bulletin_notice_api_blue.route('/add', methods=['POST'])
@login_api_check()
def add():
    access_status = judging_permissions('2_1_0')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    data = get_request_params()

    _insert(data)
    return jsonify({'code': 200, 'msg': u'success'})


@bulletin_notice_api_blue.route('/detail', methods=['GET'])
@login_api_check()
def detail():
    access_status = judging_permissions('2_1_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _id = request.args.get('_id', '')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'缺少参数'})
    _obj = bulletin_notice.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'参数错误'})
    _obj['_id'] = str(_obj.get('_id'))
    return jsonify({'code': 200, 'data': _obj})


@bulletin_notice_api_blue.route('/update', methods=['POST'])
@login_api_check()
def update():
    access_status = judging_permissions('2_1_2')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _update = {}
    data = get_request_params()
    _id = data.get('_id')
    if not ObjectId.is_valid(_id):
        return jsonify({'code': 202, 'msg': u'参数错误'})
    _obj = bulletin_notice.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'参数错误'})
    for key in default_values:
        if key == 'user_num':
            continue
        _values = data.get(key, '')
        # if isinstance(_values, str) or isinstance(_values, unicode):
        if isinstance(_values, str):
            _values = _values.strip()

        if key in int_key:
            try:
                _values = int(_values)
            except:
                return jsonify({'code': 201, 'msg': u'参数错误'})
        if _obj.get(key) != _values:
            _update.update({key: _values})
    if _update:
        try:
            _update.update({'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
            bulletin_notice.update({'_id': _obj.get('_id')}, {'$set': _update})
            bulletin_notice.update_many({}, {'$set': {'user_num': 0}})
        except:
            return jsonify({'code': 203, 'msg': u'修改失败'})
    return jsonify({'code': 200, 'msg': u'success'})


@bulletin_notice_api_blue.route('/delete', methods=['DELETE'])
@login_api_check()
def delete():
    access_status = judging_permissions('2_1_1')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    data = get_request_params()
    _id = data.get('_id', '')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 202, 'msg': u'参数错误'})
    bulletin_notice.remove({'_id': ObjectId(_id)})
    return jsonify({'code': 200, 'msg': u'success'})
