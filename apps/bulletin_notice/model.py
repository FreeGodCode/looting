# -*- coding: utf8 -*-
import copy

from pymongo.errors import DuplicateKeyError

from libs.db import bulletin_notice

default_des = {
    'title': u'通知标题',
    'des': u'描述',
    'type_num': u'跳转类型',
    'jump_url': u'目标位置',
    'start_time': u'通知开始时间',
    'end_time': u'通知结束时间',
    'status': u'状态',
    'remark': u'备注',
}

default_values = {
    'title': u'',
    'des': u'',
    'type_num': 0,
    'jump_url': u'',
    'start_time': u'',
    'end_time': u'',
    'status': 0,
    'remark': u'',
}

status_values = {
    -1: u'关闭通知',
    1: u'开启通知'
}

type_num_values = {
    0: u'文档类型',
    1: u'h5跳转',
    2: u'APP内部',
    3: u'站内消息'
}

int_key = ['status', 'type_num']

station_notice_des = {
    'title': u'通知标题',
    'des': u'描述',
    'type_num': u'补贴类型 0为没有补贴 1为补贴热量  2为补贴现金',
    'value': u'补贴金额',
    'subsidy_des': u'补贴说明',
    'created_time': u'创建时间',
    'content': u'通知内容',
    'status': u'状态  0为未读  1为已读',
    'is_bulletin': u'是否弹框  0为不弹框  1为弹框',
}


def _insert(data):
    d_value = {
        'title': u'',
        'des': u'',
        'type_num': 0,
        'jump_url': u'',
        'start_time': u'',
        'end_time': u'',
        'status': 0,
        'remark': u'',
    }
    add_dict = copy.copy(d_value)
    for key in d_value:
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
        bulletin_notice.insert_one(add_dict)
        bulletin_notice.update_many({}, {'$set': {'user_num': 0}})
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, '_id': add_dict.get('_id')}
