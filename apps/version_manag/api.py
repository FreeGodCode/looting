# -*- coding: utf8 -*-
import sys

from bson import ObjectId
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from libs.crypt import XKcrypt
from libs.db import (version_manag)
from libs.permission import permissions_check
from model import (default_values, int_key, status_values, _insert, is_upgrade_values, available_status_values)

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

version_manag_api_blue = Blueprint('version_manag_api', __name__, url_prefix='/api/version_manag')


@version_manag_api_blue.route('/my_list', methods=['get'])
@permissions_check('version:get')
def my_list():
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

    _cur = version_manag.find(criteria)
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

                _obj['status_name'] = status_values.get(_obj.get('status', 1), '-')
                _obj['is_upgrade_name'] = is_upgrade_values.get(_obj.get('is_upgrade', 1), '-')
                _obj['available_status_name'] = available_status_values.get(_obj.get('available_status', 1), '-')

                _list.append(_obj)
            except Exception as e:
                print (e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@version_manag_api_blue.route('/add', methods=['POST'])
@permissions_check('version:create')
def add():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    result = _insert(data)
    if result.get('status', False):
        return jsonify({'code': 200, 'msg': u'成功'})
    else:
        return jsonify({'code': 203, 'msg': result.get('msg', '')})


@version_manag_api_blue.route('/detail', methods=['get'])
@permissions_check('version:get')
def detail():
    _id = request.args.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = version_manag.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})

    _obj['_id'] = _id
    return jsonify({'code': 200, 'data': _obj})


@version_manag_api_blue.route('/update', methods=['post'])
@permissions_check('version:edit')
def update():
    _update = {}
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = version_manag.find_one({'_id': ObjectId(_id)})
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
            version_manag.update_one({'_id': ObjectId(_id)}, {'$set': _update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})


@version_manag_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('version:delete')
def delete():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})

    version_manag.remove({'_id': ObjectId(_id)})
    return jsonify({'code': 200, 'msg': u'成功'})


@version_manag_api_blue.route('/notice', methods=['post'])
@permissions_check('version:edit')
def notice_gzh():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = version_manag.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})

    return jsonify({'code': 200, 'msg': u'成功'})
