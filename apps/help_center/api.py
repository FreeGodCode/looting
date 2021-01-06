# -*- coding: utf8 -*-
import sys

from bson import ObjectId
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from libs.common import login_api_check, judging_permissions
from libs.crypt import XKcrypt
from libs.db import (help_center)
from libs.utils import upload_img
from model import (default_values, int_key, status_values, _insert, type_num_values, boot_area_values)

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

help_center_api_blue = Blueprint('help_center_api', __name__, url_prefix='/api/help_center')


@help_center_api_blue.route('/my_list', methods=['get'])
@login_api_check()
def my_list():
    criteria = {}
    # 支持表格字段里的任何搜索
    access_status = judging_permissions('2_2_3')
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

    _cur = help_center.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('type_num', 1), ('sort_id', 1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                _obj['s_id'] = str(_obj['_id'])
                _obj['status_name'] = status_values.get(_obj.get('status', 0), '-')
                _obj['type_num_name'] = type_num_values.get(_obj.get('type_num', 0), u'帮助文档')
                _obj['boot_area_name'] = boot_area_values.get(_obj.get('boot_area', -1), u'无区域')
                _list.append(_obj)
            except Exception as e:
                print (e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@help_center_api_blue.route('/add', methods=['POST'])
@login_api_check()
def add():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    access_status = judging_permissions('2_2_0')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _file = request.files
    img_url_file = _file.get('img_url')
    if img_url_file:
        result, img_url = upload_img(img_url_file)
        if not result:
            return jsonify({'code': 206, 'msg': img_url})
        data.update({'img_url': img_url})
    result = _insert(data)
    if result.get('status', False):
        return jsonify({'code': 200, 'msg': u'成功'})
    else:
        return jsonify({'code': 203, 'msg': result.get('msg', '')})


@help_center_api_blue.route('/detail', methods=['get'])
@login_api_check()
def detail():
    access_status = judging_permissions('2_2_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _id = request.args.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = help_center.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})

    _obj['_id'] = _id
    return jsonify({'code': 200, 'data': _obj})


@help_center_api_blue.route('/update', methods=['post'])
@login_api_check()
def update():
    access_status = judging_permissions('2_2_2')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    _update = {}
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = help_center.find_one({'_id': ObjectId(_id)})
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
    if 'img_url' in _update:
        del _update['img_url']
    _file = request.files
    img_url_file = _file.get('img_url')
    if img_url_file:
        result, img_url = upload_img(img_url_file)
        if not result:
            return jsonify({'code': 206, 'msg': img_url})
        _update.update({'img_url': img_url})
    if _update:
        try:
            help_center.update_one({'_id': ObjectId(_id)}, {'$set': _update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})


@help_center_api_blue.route('/delete', methods=['delete', 'post'])
@login_api_check()
def delete():
    access_status = judging_permissions('2_2_1')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})

    help_center.remove({'_id': ObjectId(_id)})
    return jsonify({'code': 200, 'msg': u'成功'})
