# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import role, role_authority
from libs.utils import timestamp_to_strftime

default_des = {
    'name': u'角色名字',
    'remark': u'备注',
    'created_time': u'创建时间',
    'updated_time': u'更新时间',
}

default_values = {
    'name': u'',
    'remark': u'',
    'created_time': timestamp_to_strftime(time.time()),
    'updated_time': timestamp_to_strftime(time.time())
}

int_key = []


def _insert(data, is_role=False):
    d_v = {
        'name': u'',
        'remark': u'',
        'created_time': timestamp_to_strftime(time.time()),
        'updated_time': timestamp_to_strftime(time.time())
    }
    add_dict = copy.copy(d_v)

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
                        return {'status': False, 'msg': u'参数错误'}
                add_dict.update({key: _values})
    try:
        role.insert_one(add_dict)
        if is_role:
            _id = add_dict.get('_id')
            role_authority.insert(
                [
                    {'role_id': str(_id), 'authority': 'admin:create'},
                    {'role_id': str(_id), 'authority': 'admin:delete'},
                    {'role_id': str(_id), 'authority': 'admin:edit'},
                    {'role_id': str(_id), 'authority': 'admin:get'},
                    {'role_id': str(_id), 'authority': 'admin:role_set'},
                    {'role_id': str(_id), 'authority': 'role:create'},
                    {'role_id': str(_id), 'authority': 'role:delete'},
                    {'role_id': str(_id), 'authority': 'role:edit'},
                    {'role_id': str(_id), 'authority': 'role:get'},
                    {'role_id': str(_id), 'authority': 'role:permissions_allow'},
                    {'role_id': str(_id), 'authority': 'system:edit'},
                    {'role_id': str(_id), 'authority': 'system:get'},
                ]
            )
            print _id
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('name', ascending)], 'unique': True}]:
        role.ensure_index(item.get('field'), unique=item.get('unique'))


if __name__ == '__main__':
    d_v = {
        'name': u'管理员',
        'remark': u'管理员',
        'created_time': timestamp_to_strftime(time.time()),
        'updated_time': timestamp_to_strftime(time.time())
    }
    _insert(d_v, True)
