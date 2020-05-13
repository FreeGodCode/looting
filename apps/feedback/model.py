# -*- coding: utf8 -*-
import copy
import time

from pymongo.errors import DuplicateKeyError

from libs.db import feedback
from libs.utils import timestamp_to_strftime

default_des = {
    'user_id': u'用户ID',
    'content': u'反馈内容',
    'thumbnail': u'缩略图',
    'image_list': u'图片列表',
    'contact_information': u'联系方式',
    'created_time': u'创建时间',
}

default_values = {
    'user_id': u'',
    'content': u'',
    'thumbnail': u'',
    'image_list': [],
    'contact_information': u'',
    'created_time': timestamp_to_strftime(time.time()),
}

int_key = []


def _insert(data):
    d_val = {
        'user_id': u'',
        'content': u'',
        'thumbnail': u'',
        'image_list': [],
        'contact_information': u'',
        'created_time': timestamp_to_strftime(time.time()),
    }
    add_dict = copy.copy(d_val)
    for key in default_values:
        if key in data:
            _values = data.get(key)
            if isinstance(_values, str) or isinstance(_values, unicode):
                _values = _values.strip()
            if key in int_key:
                try:
                    _values = int(_values)
                except:
                    return {'status': False, 'msg': u'参数错误'}
            add_dict.update({key: _values})
    try:
        feedback.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True}


if __name__ == '__main__':
    _insert({})
