# -*- coding: utf8 -*-
import copy

from pymongo.errors import DuplicateKeyError

from libs.db import heat_task

default_des = {
    'name': u'任务模块名字',
    'module_id': u'任务模块id',
    'sort_id': u'排序值',
    'status': u'状态',
    'remark': u'备注',
}

default_values = {
    'name': u'',
    'module_id': u'',
    'sort_id': 0,
    'status': 1,
    'remark': u'',
}

status_values = {
    -1: u'隐藏',
    1: u'显示',
}

int_key = ['status', 'sort_id']


def _insert(data):
    d_value = {
        'name': u'',
        'module_id': u'',
        'sort_id': 0,
        'status': 1,
        'remark': u'',
    }
    add_dict = copy.copy(d_value)
    for key in d_value:
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
        heat_task.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, '_id': add_dict.get('_id')}
