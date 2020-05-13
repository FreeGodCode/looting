# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import income
from libs.utils import timestamp_to_strftime

default_des = {
    'yesterday_income': u'昨日收益',
    'historical_income': u'历史收益',
    'red_pool': u'红包池',
    'created_time': u'创建时间'
}

default_values = {
    'yesterday_income': 0,
    'historical_income': 0,
    'red_pool': 0,
    'created_time': timestamp_to_strftime(time.time())
}

int_key = ['yesterday_income', 'historical_income', 'red_pool']


def _insert(data):
    d_v = {
        'yesterday_income': 0,
        'historical_income': 0,
        'red_pool': 0,
        'created_time': timestamp_to_strftime(time.time() + 24 * 60 * 60, format='%Y-%m-%d')
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
        income.insert_one(add_dict)

    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('created_time', ascending)], 'unique': True}]:
        income.ensure_index(item.get('field'), unique=item.get('unique'))
