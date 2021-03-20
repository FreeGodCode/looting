# -*- coding: utf8 -*-
# import sys

# from bson import ObjectId
from flask import Blueprint, request, jsonify

from libs.common import login_api_check, judging_permissions
from libs.db import guess_red, guess_red_detail, user
from model import (default_values, int_key, status_values)

# reload(sys)
# sys.setdefaultencoding("utf-8")

guess_red_api_blue = Blueprint('guess_red_api', __name__, url_prefix='/api/guess_red')


@guess_red_api_blue.route('/my_list', methods=['get'])
@login_api_check()
def my_list():
    access_status = judging_permissions('0_7_3')
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

    _cur = guess_red.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('today_str', -1), ('hour_int', -1), ('minute_int', -1)]).skip(page_num * limit).limit(
            limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                _obj['status_name'] = status_values.get(_obj.get('status', 0), '')
                _obj['hour_int_d'] = str(_obj.get('hour_int', 0)) + u' 点'

                _obj['value'] = '%.2f' % (float(_obj.get('value')) / float(100))
                _list.append(_obj)
            except Exception as e:
                print(e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@guess_red_api_blue.route('/detail_list', methods=['get'])
@login_api_check()
def detail_list():
    access_status = judging_permissions('0_7_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)

    guess_red_id = request.args.get('guess_red_id', '')

    criteria = {'number_of_periods': int(guess_red_id)}

    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = guess_red_detail.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                _list.append(_obj)
            except Exception as e:
                print(e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})
