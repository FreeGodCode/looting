# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import home_ad
from libs.utils import timestamp_to_strftime

default_des = {
    'name': u'入口名字',
    'img_url': u'图片地址',
    'mark': u'标记文字',
    'type_num': u'文档类型',
    'sort_id': u'排序值',
    'associated_id': u'关联热量任务的id',
    'status': u'状态',
    'remark': u'备注',
    'created_time': u'创建时间'
}

default_values = {
    'name': u'',
    'img_url': u'',
    'mark': u'',
    'type_num': 'app_insidepage',
    'associated_id': u'',
    'sort_id': 0,
    'status': 1,
    'remark': u'',
    'created_time': timestamp_to_strftime(time.time())
}

int_key = ['sort_id', 'status']

status_values = {
    -1: u'隐藏',
    1: u'显示'
}

type_num_values = {
    'daily_task': u'日常任务',
    'wake_app': u'APP唤醒',
    'app_insidepage': u'APP内页',
}


def _insert(data):
    d_v = {
        'name': u'',
        'img_url': u'',
        'mark': u'',
        'type_num': 'app_insidepage',
        'associated_id': u'',
        'sort_id': 0,
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
        home_ad.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('name', ascending)], 'unique': True},
                 {'field': [('sort_id', ascending)], 'unique': False},
                 {'field': [('status', ascending)], 'unique': False}]:
        home_ad.ensure_index(item.get('field'), unique=item.get('unique'))
