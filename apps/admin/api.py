# -*- coding: utf8 -*-
import sys

from bson import ObjectId
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash

from libs.common import login_api_check, judging_permissions
from libs.crypt import XKcrypt
from libs.db import (admin_user, login_log, role, user_role, redis_code)
from libs.permission import permissions_check
from libs.utils import timestamp_to_strftime, get_chars2, send_sms_163
from model import (default_values, int_key, _insert, status_values)

crypt_obj = XKcrypt()

import time

reload(sys)
sys.setdefaultencoding('utf-8')

admin_api_blue = Blueprint('admin_api', __name__, url_prefix='/api/admin')


@admin_api_blue.route('/my_list', methods=['get'])
@permissions_check('admin:get')
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

    _cur = admin_user.find(criteria)
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
                _obj['status_name'] = status_values.get(_obj.get('status', 0))
                role_id_list = []
                user_role_cur = user_role.find({'user_id': _obj['_id']})
                for user_role_obj in user_role_cur:
                    role_id_list.append(ObjectId(user_role_obj.get('role_id')))
                if role_id_list:
                    role_cur = role.find({'_id': {'$in': role_id_list}})
                    role_list = []
                    for role_obj in role_cur:
                        role_list.append(role_obj.get('name'))
                    if role_list:
                        _obj['role_name'] = ','.join(role_list)
                    else:
                        _obj['role_name'] = '-'
                else:
                    _obj['role_name'] = '-'
                _obj['lgoin_times'] = login_log.find({'user_id': _obj['_id']}).count()
                try:
                    _obj['lgoin_time_last'] = login_log.find({'user_id': _obj['_id']}).sort([('_id', -1)])[0].get(
                        'created_time')
                except:
                    _obj['lgoin_time_last'] = '-'
                _obj['spread_c_name'] = u'无'

                _list.append(_obj)
            except Exception, e:
                print e
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@admin_api_blue.route('/add', methods=['POST'])
@permissions_check('admin:create', True)
def add():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    user_obj = admin_user.find_one({'username': data.get('username')})
    if user_obj:
        return jsonify({'code': 202, 'msg': u'此账号已经存在，请不要重复添加'})
    result = _insert(data)
    if result.get('status', False):
        return jsonify({'code': 200, 'msg': u'成功'})
    else:
        return jsonify({'code': 203, 'msg': result.get('msg', '')})


@admin_api_blue.route('/detail', methods=['get'])
@permissions_check('admin:get')
def detail():
    _id = request.args.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = admin_user.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    _obj['_id'] = _id
    _obj['status_name'] = status_values.get(_obj.get('status', 0))
    return jsonify({'code': 200, 'data': _obj})


@admin_api_blue.route('/update', methods=['post'])
@permissions_check('admin:edit', True)
def update():
    _update = {}
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    _obj = admin_user.find_one({'_id': ObjectId(_id)})
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
            admin_user.update_one({'_id': ObjectId(_id)}, {'$set': _update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})


@admin_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('admin:delete', True)
def delete():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        return jsonify({'code': 201, 'msg': u'参数错误'})
    admin_user.remove({'_id': ObjectId(_id)})
    return jsonify({'code': 200, 'msg': u'成功'})


@admin_api_blue.route('/allot_role', methods=['post'])
@permissions_check('admin:role_set')
def allot_role():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _id = data.get('_id')
    if not _id:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    new_role_id_list = []
    for key in data:
        if data.get(key) == 'on':
            new_role_id_list.append(key)
    old_role_id_list = user_role.find({'user_id': _id}).distinct('role_id')
    for old_role_id in old_role_id_list:
        if old_role_id not in new_role_id_list:
            user_role.remove({'user_id': _id, 'role_id': old_role_id})
    for new_role_id in new_role_id_list:
        if not user_role.find_one({'user_id': _id, 'role_id': new_role_id}):
            user_role.insert_one({'user_id': _id, 'role_id': new_role_id})

    return jsonify({'code': 200, 'msg': u'成功'})


@admin_api_blue.route('/edit_list', methods=['get'])
@permissions_check('admin:get')
def edit_list():
    role_obj = role.find_one({'name': u'编辑'})
    role_id = str(role_obj.get('_id'))
    user_id_list = []
    user_role_cur = user_role.find({'role_id': role_id})
    for user_role_obj in user_role_cur:
        user_id_list.append(ObjectId(user_role_obj.get('user_id')))
    criteria = {'_id': {'$in': user_id_list}}
    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = admin_user.find(criteria)
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
                _obj['status_name'] = status_values.get(_obj.get('status', 0))
                role_id_list = []
                user_role_cur = user_role.find({'user_id': _obj['_id']})
                for user_role_obj in user_role_cur:
                    role_id_list.append(ObjectId(user_role_obj.get('role_id')))
                if role_id_list:
                    role_cur = role.find({'_id': {'$in': role_id_list}})
                    role_list = []
                    for role_obj in role_cur:
                        role_list.append(role_obj.get('name'))
                    if role_list:
                        _obj['role_name'] = ','.join(role_list)
                    else:
                        _obj['role_name'] = '-'
                else:
                    _obj['role_name'] = '-'
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


@admin_api_blue.route('/send_code', methods=['POST'])
@permissions_check('admin:edit')
def send_code():
    username = session.get('username')
    user_obj = admin_user.find_one({'username': username})
    phone = user_obj.get('phone')
    if phone:
        msg_code = get_chars2(0, 6)

        params_163 = '{"code":"' + msg_code + '"}'
        response_json = send_sms_163(phone, params_163, '10859')
        if response_json.get('code') == 200:
            # 验证码存redis
            redis_code.set(phone, msg_code, ex=int(60 * 5))
            return jsonify({'code': 200, 'msg': u'成功'})
    return jsonify({'code': 200, 'msg': u'成功'})
