# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import planet_img
from libs.utils import timestamp_to_strftime

default_des = {
    'img_url': u'图片地址',
    'remark': u'备注',
    'created_time': u'创建时间'
}

default_values = {
    'img_url': u'',
    'remark': u'',
    'created_time': timestamp_to_strftime(time.time())
}

int_key = []


def _insert(data):
    d_v = {
        'img_url': u'',
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
        planet_img.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, 'user_id': str(add_dict['_id'])}

