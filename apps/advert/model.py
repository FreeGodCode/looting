# -*- coding: utf8 -*-

from libs.db import domain_h5
from libs.pymongo_ex import get_pageable


class Model:
    @property
    def default_des(self):
        return {
            'name': u'广告名称',
            'type_num': u'广告类型',
            'entity_url': u'广告链接',
            'status': u'状态',
            'use_count': u'使用次数',
            'remark': u'备注',
        }

    @property
    def default_values(self):
        return {
            'name': u'',
            'type_num': 0,
            'entity_url': u'',
            'status': 0,
            'use_count': 0,
            'remark': u'',
        }

    status_values = {
        0: u'禁用',
        1: u'正常',
    }
    type_num_values = {
        0: u'图片广告',
        1: u'视频广告'
    }

    int_keys = ['type_num', 'status', 'use_count']


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
