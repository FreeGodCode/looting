# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import version_manag
from libs.utils import timestamp_to_strftime

default_des = {
    'name': u'版本名字',
    'content': u'更新内容',
    'version_num': u'版本号',
    'system_type': u'系统型号',
    'is_upgrade': u'是否强制性升级',
    'available_status': u'可用状态',
    'download_url': u'下载地址',
    'status': u'状态',
    'remark': u'备注',
    'created_time': u'创建时间'
}

default_values = {
    'name': u'',
    'content': u'',
    'version_num': u'',
    'system_type': u'',
    'is_upgrade': 1,
    'available_status': 1,
    'download_url': u'',
    'status': 1,
    'remark': u'',
    'created_time': timestamp_to_strftime(time.time())
}

int_key = ['is_upgrade', 'available_status', 'status']

is_upgrade_values = {
    -1: u'不强制性升级',
    1: u'强制性升级'
}
available_status_values = {
    -1: u'关闭不可用',
    1: u'正常可用'
}

status_values = {
    -1: u'审核版本',
    1: u'正常版本'
}


def _insert(data):
    d_v = {
        'name': u'',
        'content': u'',
        'version_num': u'',
        'system_type': u'',
        'is_upgrade': 1,
        'available_status': 1,
        'download_url': u'',
        'status': 1,
        'remark': u'',
        'created_time': timestamp_to_strftime(time.time())
    }
    add_dict = copy.copy(d_v)

    for key in default_values:
        if key in data:
            _values = data.get(key)
            if _values:
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
        version_manag.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}


def start_create_index():
    ascending = 1
    for item in [{'field': [('name', ascending)], 'unique': False},
                 {'field': [('version_num', ascending)], 'unique': False},
                 {'field': [('status', ascending)], 'unique': False}]:
        version_manag.ensure_index(item.get('field'), unique=item.get('unique'))
