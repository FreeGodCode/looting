# -*- coding: utf8 -*-
from libs.common import get_datetime_str
from libs.db import product
from libs.pymongo_ex import get_pageable


class Model:
    @property
    def default_des(self):
        return {
            'thumbnail_url': u'商品缩略图',
            'image_list': u'商品大图集合',
            'name': u'商品名称',
            'description': u'商品描述',
            'worth_value': u'商品价值',
            'stock_num': u'商品库存数量',
            'created_time': u'商品录入时间',
            'sort_num': u'排序值',
            'status': u'状态',
            'remark': u'备注',
            'rules': u'玩法规则',
            'pv_count': u'展示次数',
            'use_count': u'使用次数',
            'disabled': u'禁止'
        }

    @property
    def default_values(self):
        return {
            'thumbnail_url': u'',
            'image_list': u'',
            'name': u'',
            'description': u'',
            'worth_value': 0,
            'stock_num': 0,
            'created_time': get_datetime_str(),
            'sort_num': 0,
            'status': 0,
            'remark': u'',
            'rules': u'',
            'pv_count': 0,
            'use_count': 0,
            'disabled': 0
        }

    status_values = {
        0: u'隐藏',
        1: u'显示'
    }

    int_keys = [
        'worth_value',
        'stock_num',
        'sort_num',
        'status',
        'pv_count',
        'use_count',
        'disabled'
    ]


model = Model()


def product_info_processor(product_obj):
    return product_obj


def get_list_obj(criteria, page_num, limit):
    criteria['disabled'] = 0
    _cur = product.find(criteria).sort([('_id', -1)])
    page_obj = get_pageable(_cur, page_num, limit, processor=product_info_processor)
    return page_obj


def create_obj(data):
    product.insert(data)
    return True


def get_detail_obj(_id):
    detail_obj = product.find_one({'_id': _id})
    return detail_obj


def update_obj(_id, data):
    product.update_one({'_id': _id}, {'$set': data})
    return True


def delete_obj(_id):
    product.update_one({'_id': _id}, {'$set': {'disabled': 1}})
    return True
