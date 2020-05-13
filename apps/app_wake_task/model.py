# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import app_wake_task
from libs.utils import timestamp_to_strftime

default_des = {
    'name': u'APP名字',
    'img_url': u'APP图片',
    'task_type': u'任务类型',
    'android_package_name': u'安卓包名',
    'ios_url_scheme': u'ios检测是否下载地址',
    'app_download_url': u'APP下载地址',
    'jump_url': u'跳转目标地址',
    'start_time': u'任务开始时间',
    'end_time': u'任务结束时间',
    'heat_value': u'奖励热量的值',
    'heat_times': u'奖励热量的次数',
    'sort_id': u'排序值',
    'status': u'状态',
    'open_system': u'开放系统',
    'remark': u'备注',
    'created_time': u'创建时间'
}

default_values = {
    'name': u'',
    'img_url': u'',
    'task_type': u'app_wake',
    'android_package_name': u'',
    'ios_url_scheme': u'',
    'app_download_url': u'',
    'jump_url': u'',
    'start_time': u'',
    'end_time': u'',
    'heat_value': 5,
    'heat_times': 1,
    'sort_id': 0,
    'status': 0,
    'open_system': 0,
    'remark': u'',
    'created_time': timestamp_to_strftime(time.time())
}

int_key = ['sort_id', 'status', 'heat_value', 'heat_times', 'open_system']

status_values = {
    -1: u'隐藏',
    1: u'显示'
}
open_system_values = {
    0: u'全部开放',
    1: u'只开放IOS',
    2: u'只开放android'
}


def _insert(data):
    d_v = {
        'name': u'',
        'img_url': u'',
        'task_type': u'app_wake',
        'android_package_name': u'',
        'ios_url_scheme': u'',
        'app_download_url': u'',
        'jump_url': u'',
        'start_time': u'',
        'end_time': u'',
        'heat_value': 5,
        'heat_times': 1,
        'sort_id': 0,
        'status': 0,
        'open_system': 0,
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
        app_wake_task.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('name', ascending)], 'unique': True},
                 {'field': [('sort_id', ascending)], 'unique': False},
                 {'field': [('status', ascending)], 'unique': False}]:
        app_wake_task.ensure_index(item.get('field'), unique=item.get('unique'))
