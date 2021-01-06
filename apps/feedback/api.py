# -*- coding: utf8 -*-
import sys
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify

from libs.common import login_api_check, judging_permissions
from libs.db import feedback, user, station_notice
from model import (default_values, int_key)

# reload(sys)
# sys.setdefaultencoding("utf-8")

feedback_api_blue = Blueprint('feedback_api', __name__, url_prefix='/api/feedback')


@feedback_api_blue.route('/my_list', methods=['get'])
@login_api_check()
def my_list():
    access_status = judging_permissions('1_2_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    criteria = dict()
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

    _cur = feedback.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('created_time', -1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                user_id = _obj.get('user_id')
                user_obj = user.find_one({'_id': ObjectId(user_id)})
                _obj['nickname'] = user_obj.get('nickname')
                _obj['phone'] = user_obj.get('phone', u'暂未绑定手机')
                _obj['is_reply'] = u'未回复'
                if station_notice.find_one({'feedback_id': _obj.get('_id')}):
                    _obj['is_reply'] = u'已回复'
                _list.append(_obj)
            except Exception as e:
                print (e)

        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@feedback_api_blue.route('/detail', methods=['get'])
@login_api_check()
def get_detail():
    access_status = judging_permissions('1_2_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _id = request.args.get('_id')
    if not _id:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = feedback.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    _obj['_id'] = _id
    content = _obj.get('content')
    image_list = _obj.get('image_list')
    for inage_url in image_list:
        content += '<p><img src="' + inage_url + '></p>'
    return jsonify({'code': 200, 'data': _obj})


@feedback_api_blue.route('/delete', methods=['post'])
@login_api_check()
def delete():
    access_status = judging_permissions('1_2_1')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    feedback.remove({'_id': ObjectId(_id)})
    return jsonify({'code': 200, 'msg': u'成功'})


@feedback_api_blue.route('/reply', methods=['post'])
@login_api_check()
def feedback_reply():
    access_status = judging_permissions('1_2_2')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    notice_content = data.get('station_notice')
    if not _id or not notice_content:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    feedback_obj = feedback.find_one({'_id': ObjectId(_id)})
    user_id = feedback_obj.get('user_id')
    station_notice.insert_one({'user_id': user_id, 'title': u'意见反馈回复', 'des': notice_content[:10] + '......',
                               'type_num': 0, 'value': 0, 'content': notice_content, 'status': 0, 'is_bulletin': 0,
                               'subsidy_des': '', 'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S'),
                               'feedback_id': _id})

    return jsonify({'code': 200, 'msg': u'成功'})
