# -*- coding: utf8 -*-
import sys

from bson import ObjectId
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from libs.common import login_api_check, judging_permissions
from libs.crypt import XKcrypt
from libs.db import (admin_user, user_role, login_log, role, role_authority)
from libs.permission import permissions_check
from libs.utils import timestamp_to_strftime
from model import (default_values, int_key, _insert)

crypt_obj = XKcrypt()

import time

reload(sys)
sys.setdefaultencoding('utf-8')

role_api_blue = Blueprint('role_api', __name__, url_prefix='/api/role')


@role_api_blue.route('/my_list', methods=['get'])
@permissions_check('role:get')
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

    _cur = role.find(criteria)
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
                user_id_list = []
                user_role_cur = user_role.find({'role_id': _obj['_id']})
                for user_role_obj in user_role_cur:
                    user_id_list.append(ObjectId(user_role_obj.get('user_id')))
                if user_id_list:
                    user_cur = admin_user.find({'_id': {'$in': user_id_list}, 'status': 0})
                    user_list = []
                    for user_obj in user_cur:
                        user_list.append(user_obj.get('real_name'))
                    if user_list:
                        _obj['user_name'] = ','.join(user_list)
                    else:
                        _obj['user_name'] = '-'
                else:
                    _obj['user_name'] = '-'
                _obj['lgoin_times'] = login_log.find({'user_id': _obj['_id']}).count()
                try:
                    _obj['lgoin_time_last'] = login_log.find({'user_id': _obj['_id']}).sort([('_id', -1)])[0].get(
                        'created_time')
                except:
                    _obj['lgoin_time_last'] = '-'
                _list.append(_obj)
            except Exception, e:
                print e
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@role_api_blue.route('/add', methods=['POST'])
@permissions_check('role:get', False)
def add():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    role_obj = role.find_one({'name': data.get('name')})
    if role_obj:
        return jsonify({'code': 202, 'msg': u'此角色已经存在，请不要重复添加'})
    result = _insert(data)
    if result.get('status', False):
        return jsonify({'code': 200, 'msg': u'成功'})
    else:
        return jsonify({'code': 203, 'msg': result.get('msg', '')})


@role_api_blue.route('/detail', methods=['get'])
@permissions_check('role:get')
def detail():
    _id = request.args.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = role.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    _obj['_id'] = _id
    return jsonify({'code': 200, 'data': _obj})


@role_api_blue.route('/update', methods=['post'])
@permissions_check('role:get', False)
def update():
    _update = {}
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = role.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    for key in default_values:
        if key in data:
            _values = data.get(key)
            if _values:
                if isinstance(_values, str) or isinstance(_values, unicode):
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
        _update.update({'updated_time': timestamp_to_strftime(time.time())})
        try:
            role.update_one({'_id': ObjectId(_id)}, {'$set': _update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})


@role_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('role:delete')
def delete():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    role.remove({'_id': ObjectId(_id)})
    return jsonify({'code': 200, 'msg': u'成功'})


@role_api_blue.route('/allot_authority', methods=['post'])
@permissions_check('role:permissions_allow', False)
def allot_authority():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    new_authority_list = []
    for key in data:
        if data.get(key) == 'on':
            new_authority_list.append(key)
    old_authority_list = role_authority.find({'role_id': _id}).distinct('authority')
    for old_authority in old_authority_list:
        if old_authority not in new_authority_list:
            role_authority.remove({'role_id': _id, 'authority': old_authority})
    for new_authority in new_authority_list:
        if not role_authority.find_one({'role_id': _id, 'authority': new_authority}):
            role_authority.insert_one({'role_id': _id, 'authority': new_authority})
    return jsonify({'code': 200, 'msg': u'成功'})
