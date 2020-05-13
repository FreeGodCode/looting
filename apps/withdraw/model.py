# -*- coding: utf8 -*-
from datetime import datetime

from libs.common import get_user_by_id, get_datetime_str
from libs.db import withdraw_record, withdraw_order
from libs.exception_ex import ProcessError
from libs.pymongo_ex import get_pageable

default_des = {
    'serial_number': u'提现流水号',
    'user_id': u'用户id',
    'nickname': u'用户昵称',
    'bind_mobile': u'绑定手机号码',
    'headimgurl': u'用户头像',
    'type_num': u'提现类型',
    'value': u'提现金额(单位分)',
    'origin': u'提现说明',
    'status': u'提现状态',
    'alipay_name': u'支付宝账号真实姓名',
    'alipay_phone': u'支付宝账号',
    'alipay_account': u'支付宝账号',
    'weixin_qrcode': u'微信收款二维码',
    'balance': u'流水后的余额',
    'remark': u'审核备注',
    'review_time': u'审核时间',
    'review_name': u'审核人',
    'err_code': '',
    'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')
}

default_values = {
    'serial_number': u'',
    'user_id': u'',
    'nickname': u'',
    'bind_mobile': u'',
    'headimgurl': u'',
    'type_num': 1,
    'value': 0,
    'origin': u'',
    'status': 0,
    'alipay_name': u'',
    'alipay_account': u'',
    'weixin_qrcode': u'',
    'remark': u'',
    'balance': 0,
    'review_time': u'',
    'review_name': u'',
    'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')
}

int_keys = ['type_num', 'value', 'status']

type_num_values = {
    0: u'新手提现体验',
    1: u'正常提现',
    2: u'活动提现'
}
status_values = {
    -2: u'非法的提现订单',
    -1: u'审核失败',
    0: u'审核中',
    1: u'已完成'
}

payment_mode_values = {
    0: u'微信提现',
    1: u'支付宝提现',

}


def get_user_dict(user_id):
    return get_user_by_id(user_id)


def withdraw_info_processor(withdraw_obj):
    user_id = withdraw_obj['user_id']
    _obj = get_user_dict(user_id)
    _obj.update(withdraw_obj)
    _obj['value'] = _obj['worth_value']
    status = _obj['status']
    _obj['status_name'] = status_values.get(status)
    mode = _obj['payment_mode']
    _obj['origin'] = payment_mode_values.get(mode)
    type_num = _obj['type_num']
    _obj['type_num_name'] = type_num_values.get(type_num)
    return _obj


def get_withdraw_order_list(criteria, page_num, limit):
    _cur = withdraw_order.find(criteria)
    page_obj = get_pageable(_cur, page_num, limit, withdraw_info_processor)
    return page_obj


def get_withdraw_order_detail(_id):
    order_obj = withdraw_order.find_one({'_id': _id})
    return order_obj


def set_audit_success(auditor_name, order_id):
    update_dict = {
        'status': 1,
        'review_time': get_datetime_str(),
        'review_name': auditor_name,
    }
    result = withdraw_order.update_one({'_id': order_id, 'status': 0}, {'$set': update_dict})
    if result.modified_count == 0:
        raise ProcessError(10005, '数据库更新失败')


def set_audit_fail(auditor_name, order_id, fail_msg):
    update_dict = {
        'status': -1,
        'remark': fail_msg,
        'review_time': get_datetime_str(),
        'review_name': auditor_name,
    }
    result = withdraw_order.update_one({'_id': order_id, 'status': 0}, {'$set': update_dict})
    if result.modified_count == 0:
        raise ProcessError(10005, '数据库更新失败')


def start_create_index():
    ascending = 1
    for item in [{'field': [('user_id', ascending)], 'unique': False},
                 {'field': [('status', ascending)], 'unique': False}]:
        withdraw_record.ensure_index(item.get('field'), unique=item.get('unique'))
