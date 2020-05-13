# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import help_center
from libs.utils import timestamp_to_strftime

default_des = {
    'name': u'文档标题',
    'content': u'文档内容',
    'img_url': u'图片地址',
    'type_num': u'文档类型',
    'boot_area': u'引导区域',
    'sort_id': u'排序值',
    'status': u'状态',
    'remark': u'文档描述',
    'client_id': u'客户端固定ID',
    'created_time': u'创建时间'
}

default_values = {
    'name': u'',
    'des': u'',
    'content': u'',
    'img_url': u'',
    'type_num': 0,
    'boot_area': 0,
    'sort_id': 0,
    'status': 1,
    'remark': u'',
    'client_id': u'',
    'created_time': timestamp_to_strftime(time.time())
}

int_key = ['sort_id', 'status', 'type_num', 'boot_area']

status_values = {
    -1: u'隐藏',
    1: u'显示'
}
type_num_values = {
    0: u'帮助文档',
    1: u'系统公告',
    2: u'关于热量星球'
}

boot_area_values = {
    -1: u'无区域',
    0: u'热量页面',
    1: u'文章收益',
    2: u'我的收益',
    3: u'提现页面',
    4: u'整点红包',
    5: u'如何转发赚钱'
}


def _insert(data):
    d_v = {
        'name': u'',
        'content': u'',
        'img_url': u'',
        'type_num': 0,
        'boot_area': -1,
        'sort_id': 1,
        'status': 1,
        'remark': u'',
        'client_id': u'',
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
        help_center.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('name', ascending)], 'unique': True},
                 {'field': [('sort_id', ascending)], 'unique': False},
                 {'field': [('status', ascending)], 'unique': False}]:
        help_center.ensure_index(item.get('field'), unique=item.get('unique'))
