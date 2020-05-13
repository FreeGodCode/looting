# -*- coding: utf8 -*-
import copy

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from libs.common import get_datetime_str, get_user_by_id
from libs.db import planet_img, product, daily_new, flash_sale, order
from libs.exception_ex import ProcessError

default_des = {
    'order_num': u'订单号',
    'commodity_id': u'商品id',
    'user_id': u'用户id',
    'issue_num': u'期号',
    'status': u'状态',
    'status_name': u'状态名称',
    'created_time': u'创建时间',
    'today': u'创建日期',
    'channel_id': u'渠道',
    'gained_time': u'获取时间',
    'to_addr_info': {
        'name': u'收货人姓名',
        'mobile': u'收货人手机',
        'province': u'省',
        'city': u'市',
        'district': u'区',
        'address': u'详细地址'
    }
}

status_values = {
    0: u'待发货',
    1: u'已发货',
    2: u'已送达',
}

default_values = {
    'order_num': u'订单号',
    'commodity_id': u'商品id',
    'user_id': u'用户id',
    'issue_num': u'期号',
    'status': u'状态',
    'status_name': u'状态名称',
    'created_time': u'创建时间',
    'today': u'创建日期',
    'channel_id': u'渠道',
    'gained_time': u'获取时间',
    'to_addr_info': {
        'name': u'收货人姓名',
        'mobile': u'收货人手机',
        'province': u'省',
        'city': u'市',
        'district': u'区',
        'address': u'详细地址'
    }
}

int_keys = ['issue_num', 'channel_id', 'status']


def _insert(data):
    d_v = {
        'order_num': '',
        'commodity_id': '',
        'user_id': '',
        'issue_num': '',
        'status': 0,
        'status_name': '',
        'created_time': get_datetime_str('%Y-%m-%d %H:%M:%S'),
        'today': get_datetime_str('%Y-%m-%d'),
        'channel_id': 0,
        'gained_time': '',
        'to_addr_info': {
            'name': u'',
            'mobile': u'',
            'province': u'',
            'city': u'',
            'district': u'',
            'address': u''
        }
    }
    add_dict = copy.copy(d_v)

    for key in default_values:
        if key in data:
            _values = data.get(key)
            if _values:
                if isinstance(_values, str) or isinstance(_values, unicode):
                    _values = _values.strip()
                if key in int_keys:
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


product_reserved_fields = {
    '_id': 0, 'thumbnail_url': 1, 'image_url': 1, 'name': 1, 'worth_value': 1
}

CHANNEL_DAILY_NEW = 0
CHANNEL_FLASH_SALE = 1


def get_product_dict(product_id):
    """
    获取商品信息
    :param product_id:
    :return:
    """
    product_obj = product.find_one({'_id': ObjectId(product_id)}, product_reserved_fields)
    if not product_obj:
        raise ProcessError(10003, u'没有找到对象', product_id)
    return product_obj


def get_commodity_dict(commodity_id, issue_num, channel_id):
    if channel_id == CHANNEL_DAILY_NEW:
        commodity_obj = daily_new.find_one({'_id': ObjectId(commodity_id), 'issue_num': issue_num},
                                           {'_id': 0, 'status': 0})
    elif channel_id == CHANNEL_FLASH_SALE:
        commodity_obj = flash_sale.find_one({'_id': ObjectId(commodity_id), 'issue_num': issue_num},
                                            {'_id': 0, 'status': 0})
    else:
        raise ProcessError(10003, u'不支持此类型')
    if not commodity_obj:
        raise ProcessError(10003, u'为找到此订单的商品信息')
    return commodity_obj


def order_info_processor(order_obj):
    """
    商品处理器,用于获取上新商品时，补充属性
    :param product_obj:
    :return:
    """
    commodity_id = order_obj['commodity_id']
    channel_id = order_obj['channel_id']
    issue_num = order_obj['issue_num']

    commodity_obj = get_commodity_dict(commodity_id, issue_num, channel_id)
    product_id = commodity_obj['product_id']
    _obj = get_product_dict(product_id)

    # 用上新奖品属性覆盖商品属性
    _obj.update(commodity_obj)
    _obj.update(order_obj)

    status_des = [
        u'准备发货中，请耐心等候。',
        u'已发送，等耐心等待。',
        u'已送达，请查看物流信息收取你的商品。'
    ]
    status = _obj['status']
    _obj['status_name'] = status_values.get(status)
    user_obj = get_user_by_id(_obj['user_id'])
    _obj['title'] = _obj['title'] or _obj['name']
    _obj['user_name'] = user_obj['nickname']
    _obj['consignee_name'] = _obj['to_addr_info']['name']
    _obj['consignee_mobile'] = _obj['to_addr_info']['mobile']
    _obj['_id'] = str(_obj['_id'])
    return _obj


def get_order_info(order_id):
    order_obj = order.find_one({'_id': order_id})
    return order_info_processor(order_obj)
