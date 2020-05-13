# -*- coding: utf8 -*-
import functools

from flask import session, jsonify

from libs.common import login_api_check
from libs.db import admin_user, user_role, role_authority

values = {
    'primary_menu_idx': -1,
    'children_menu_idx': 0,
    'permission_menu_idx': 0
}

# 权限映射
permission_map = {
    0: ['add', 'create', 'refresh', 'upload'],  # refresh?
    1: ['delete', 'remove'],
    2: ['edit', 'update'],
    3: ['list', 'detail', 'get'],
    4: ['allotRole', 'allotAuthority']

}
# 菜单对应映射
menu_map = {}


def get_permission_idx(name):
    for key in permission_map.keys():
        for item in permission_map[key]:
            if item == name:
                return key
    return None


def get_authority(permission):
    data = permission.split(':')
    menu_name = ':'.join(data[:-1])
    permission_name = data[-1]
    return '{0}_{1}_{2}'.format(menu_map[menu_name][0], menu_map[menu_name][1], get_permission_idx(permission_name))


def value_template(val_dict):
    return '{0}_{1}_{2}'.format(val_dict['primary_menu_idx'], val_dict['children_menu_idx'],
                                val_dict['permission_menu_idx'])


def push_menu_map(name, primary_idx, children_idx):
    _list = menu_map.get(name, [])
    if _list:
        raise Exception('重复添加:{0} p:{1} c:{2}'.format(name, primary_idx, children_idx))
    for p_idx, c_idx in _list:
        if primary_idx == p_idx and children_idx == c_idx:
            raise Exception('重复添加:{0} p:{1} c:{2}'.format(name, primary_idx, children_idx))
    menu_map.update({name: (primary_idx, children_idx)})


def primary_inc(val_dict, name, val=0):
    val_dict['primary_menu_idx'] += 1
    val_dict['children_menu_idx'] = 0
    val_dict['permission_menu_idx'] = val
    val_dict['name'] = name
    push_menu_map(name, val_dict['primary_menu_idx'], val_dict['children_menu_idx'])
    return value_template(val_dict)


def children_inc(val_dict, name, val=0):
    val_dict['children_menu_idx'] += 1
    val_dict['permission_menu_idx'] = val
    val_dict['name'] = name
    push_menu_map(name, val_dict['primary_menu_idx'], val_dict['children_menu_idx'])
    return value_template(val_dict)


def permission_inc(val_dict, val=1):
    val_dict['permission_menu_idx'] += val
    return value_template(val_dict)


def permissions_check(permissions, code_verif=False):
    def decotorate(func):
        @functools.wraps(func)
        @login_api_check(code_verif)  # permissions_check 依赖 login_api_check,因此集成login_api_check
        def wrapper(*args, **kwargs):
            username = session.get('username')
            user_obj = admin_user.find_one({'username': username, 'status': 0})
            if not user_obj:
                return jsonify({'code': 230, 'msg': u'当前未登录，无法访问'})
            for perm_name in permissions.split('|'):
                role_id_list = user_role.find({'user_id': str(user_obj.get('_id'))}).distinct('role_id')
                result = role_authority.find_one({'role_id': {'$in': role_id_list}, 'authority': perm_name})
                if not result:
                    return jsonify({'code': 208, 'msg': u'您无此操作权限，如想操作请联系管理员'})
            return func(*args, **kwargs)

        return wrapper

    return decotorate
