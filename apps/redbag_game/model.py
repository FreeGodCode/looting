# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import redbag_game
from libs.utils import timestamp_to_strftime

default_des = {
    'name': u'玩法名字',
    'img_url': u'图片地址',
    'type_num': u'类型',
    'des': u'玩法描述',
    'button_txt': u'按钮文字',
    'sort_id': u'排序值',
    'template_id': u'客户端模板ID',
    'is_online': u'是否上线',
    'status': u'状态',
    'remark': u'备注',
    'created_time': u'创建时间'
}

default_values = {
    'name': u'',
    'img_url': u'',
    'type_num': 0,
    'des': u'',
    'button_txt': u'',
    'sort_id': 0,
    'template_id': u'',
    'is_online': 0,
    'status': 1,
    'remark': u'',
    'created_time': timestamp_to_strftime(time.time())
}

int_key = ['type_num', 'sort_id', 'is_online', 'status']

type_num_values = {
    0: u'老玩法',
    1: u'新玩法'
}

is_online_values = {
    0: u'未上线',
    1: u'已上线'
}

status_values = {
    -1: u'隐藏',
    1: u'显示'
}


def _insert(data):
    d_v = {
        'name': u'',
        'img_url': u'',
        'type_num': 0,
        'des': u'',
        'button_txt': u'',
        'sort_id': 0,
        'template_id': u'',
        'is_online': 0,
        'status': 1,
        'remark': u'',
        'created_time': timestamp_to_strftime(time.time())
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
        redbag_game.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('name', ascending)], 'unique': True},
                 {'field': [('sort_id', ascending)], 'unique': False},
                 {'field': [('status', ascending)], 'unique': False}]:
        redbag_game.ensure_index(item.get('field'), unique=item.get('unique'))
