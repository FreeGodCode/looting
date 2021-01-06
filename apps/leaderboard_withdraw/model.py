# -*- coding: utf8 -*-
import copy

from pymongo.errors import DuplicateKeyError

from libs.db import leaderboard_withdraw

default_des = {
    'user_id': u'用户id',
    'nickname': u'昵称',
    'phone': u'用户绑定手机',
    'withdraw_value': u'当前用户的提现金额',
    'balance': u'当前用户的余额',
    'reg_time': u'注册时间',
    'status': u'状态',
}

default_values = {
    'user_id': u'',
    'nickname': u'',
    'phone': '',
    'withdraw_value': 0,
    'balance': 0,
    'reg_time': '',
    'status': 0,
}

status_values = {
    -1: u'封禁',
    0: u'显示',
}

int_key = ['status', 'balance']


def _insert(data):
    global default_values
    add_dict = copy.copy(default_values)
    for key in default_values:
        if key in data:
            _values = data.get(key)
            # if isinstance(_values, str) or isinstance(_values, unicode):
            if isinstance(_values, str):
                _values = _values.strip()
            if key in int_key:
                try:
                    _values = int(_values)
                except:
                    return {'status': False, 'msg': u'参数错误'}
            add_dict.update({key: _values})
    try:
        leaderboard_withdraw.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True}


if __name__ == '__main__':
    _insert({})
