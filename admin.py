# -*- coding: utf8 -*-
import time

from werkzeug.security import generate_password_hash

from libs.db import role, user_role, admin_user, role_authority
from libs.utils import timestamp_to_strftime

if __name__ == '__main__':

    role_dict = {
        'name': u'管理员',
        'remark': u'管理员',
        'created_time': timestamp_to_strftime(time.time()),
        'updated_time': timestamp_to_strftime(time.time())
    }

    role_id = role.update_one(role_dict, {'$set': role_dict}, upsert=True).upserted_id
    if not role_id:
        role_id = role.find_one()['_id']

    permissions = [
        {'role_id': str(role_id), 'authority': 'admin:create'},
        {'role_id': str(role_id), 'authority': 'admin:delete'},
        {'role_id': str(role_id), 'authority': 'admin:edit'},
        {'role_id': str(role_id), 'authority': 'admin:get'},
        {'role_id': str(role_id), 'authority': 'admin:role_set'},
        {'role_id': str(role_id), 'authority': 'role:create'},
        {'role_id': str(role_id), 'authority': 'role:delete'},
        {'role_id': str(role_id), 'authority': 'role:edit'},
        {'role_id': str(role_id), 'authority': 'role:get'},
        {'role_id': str(role_id), 'authority': 'role:permissions_allow'},
        {'role_id': str(role_id), 'authority': 'system:edit'},
        {'role_id': str(role_id), 'authority': 'system:get'},
    ]
    if role_authority.count({'role_id': str(role_id)}) == 0:
        role_authority.insert_many(permissions)

    user_dict = {
        'username': u'yqf_admin',
        'password': u'yiqifu%914@4185^6',
        'real_name': u'易起富',
        'phone': u'18926445436',
        'status': 0,
        'created_time': timestamp_to_strftime(time.time()),
        'updated_time': timestamp_to_strftime(time.time())
    }
    user_dict['password'] = generate_password_hash(user_dict['password'])
    user_id = admin_user.update_one({'username': user_dict['username']}, {'$set': user_dict}, upsert=True).upserted_id
    if not user_id:
        user_id = admin_user.find_one()['_id']

    user_role_dict = {
        'user_id': str(user_id),
        'role_id': str(role_id)
    }
    user_role.update_one(user_role_dict, {'$set': user_role_dict}, upsert=True)
