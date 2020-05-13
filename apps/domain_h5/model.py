# -*- coding: utf8 -*-

from libs.db import domain_h5
from libs.pymongo_ex import get_pageable


class Model:
    @property
    def default_des(self):
        return {
            'domain': u'域名',
            'status': u'状态',
            'user_num': u'使用次数',
            'remark': u'备注',
        }

    @property
    def default_values(self):
        return {
            'domain': u'',
            'status': 1,
            'user_num': 0,
            'remark': u'',
        }

    status_values = {
        -1: u'备案掉了',
        0: u'封禁',
        1: u'正常',
        2: u'备用',
    }
    int_keys = ['status', 'user_num']

model = Model()

def domain_info_processor(domain_obj):
    return domain_obj


def get_list_obj(criteria, page_num, limit):
    _cur = domain_h5.find(criteria)
    page_obj = get_pageable(_cur, page_num, limit, processor=domain_info_processor)
    return page_obj


def get_detail_obj(_id):
    detail_obj = domain_h5.find_one({'_id': _id})
    return detail_obj


def create_obj(data):
    domain_h5.insert(data)
    return True


def update_obj(_id, data):
    domain_h5.update_one({'_id': _id}, {'$set': data})
    return True


def delete_obj(_id):
    domain_h5.delete_one({'_id': _id})
    return True
