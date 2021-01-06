# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash

from libs.db import admin_user, user_role
from libs.utils import timestamp_to_strftime

default_des = {
    'username': u'登录账号',
    'password': u'密码',
    'real_name': u'用户姓名',
    'phone': u'绑定手机号码',
    'status': u'用户状态',
    'created_time': u'创建时间',
    'updated_time': u'更新时间',
}

default_values = {
    'username': u'',
    'password': u'',
    'real_name': u'',
    'phone': u'',
    'status': 0,
    'created_time': timestamp_to_strftime(time.time()),
    'updated_time': timestamp_to_strftime(time.time())
}

int_key = ['status']

status_values = {
    0: u'正常',
    1: u'封禁',
}


def _insert(data, role_id=''):
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return {'status': False, 'msg': u'缺少参数'}
    d_v = {
        'username': u'',
        'password': u'',
        'real_name': u'',
        'phone': u'',
        'status': 0,
        'created_time': timestamp_to_strftime(time.time()),
        'updated_time': timestamp_to_strftime(time.time())
    }
    add_dict = copy.copy(d_v)
    data.update({
        'password': generate_password_hash(password),
    })

    for key in default_values:
        if key in data:
            _values = data.get(key)
            if _values:
                # if isinstance(_values, str) or isinstance(_values, unicode):
                if isinstance(_values, str):
                # if _values is isinstance(object, str):
                    _values = _values.strip()
                if key in int_key:
                    try:
                        _values = int(_values)
                    except:
                        return {'status': False, 'msg': u'参数错误'}
                add_dict.update({key: _values})
    try:
        admin_user.insert_one(add_dict)
        _id = add_dict.get('_id')
        if role_id:
            user_role.insert_one({'user_id': str(_id), 'role_id': role_id})
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('spread_c_id', ascending)], 'unique': False},
                 {'field': [('username', ascending)], 'unique': True},
                 {'field': [('status', ascending)], 'unique': False}]:
        admin_user.ensure_index(item.get('field'), unique=item.get('unique'))


if __name__ == '__main__':
    d_v = {
        'username': u'wqh',
        'password': u'123456',
        'real_name': u'易起富',
        'phone': u'18926445436',
        'status': 0,
        'created_time': timestamp_to_strftime(time.time()),
        'updated_time': timestamp_to_strftime(time.time())
    }
    _insert(d_v, '5e7098af1d47be1df44634b5')
