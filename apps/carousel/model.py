# -*- coding: utf8 -*-
import time

from libs.db import carousel, configs, CONFIG_TYPE_APP_ROUTE
from libs.pymongo_ex import get_pageable
from libs.utils import timestamp_to_strftime


class Model:
    @property
    def default_des(self):
        return {
            'name': u'轮播名字',
            'content': u'轮播内容',
            'img_url': u'图片地址',
            'route_id': u'路由id',
            'genre': u'类型',
            'sort_id': u'排序值',
            'status': u'状态',
            'remark': u'备注',
            'created_time': u'创建时间'
        }

    @property
    def default_values(self):
        return {
            'name': u'',
            'content': u'',
            'img_url': u'',
            'route_id': u'',
            'genre': 0,
            'sort_id': 0,
            'status': 1,
            'remark': u'',
            'created_time': timestamp_to_strftime(time.time())
        }

    int_keys = ['genre', 'sort_id', 'status']

    genre_values = {
        0: u'本身内容',
        1: u'APP内页',
        2: u'H5地址',
        3: u'文档类型',

    }
    status_values = {
        -1: u'隐藏',
        1: u'显示'
    }


model = Model()


def carousel_info_processor(carousel_obj):
    carousel_obj['genre_name'] = model.genre_values.get(carousel_obj['genre'])
    carousel_obj['status_name'] = model.status_values.get(carousel_obj['status'])
    route_id = carousel_obj.get('route_id', '')
    route_name = u'无'
    if route_id:
        route_obj = configs.find_one({'_id': route_id, 'type_num': CONFIG_TYPE_APP_ROUTE})
        route_name = route_obj['name']
    carousel_obj['route_name'] = route_name
    return carousel_obj


def get_list_obj(criteria, page_num, limit):
    _cur = carousel.find(criteria)
    page_obj = get_pageable(_cur, page_num, limit, processor=carousel_info_processor)
    return page_obj


def create_obj(data):
    carousel.insert(data)
    return True


def get_detail_obj(_id):
    detail_obj = carousel.find_one({'_id': _id})
    return detail_obj


def update_obj(_id, data):
    carousel.update_one({'_id': _id}, {'$set': data})
    return True


def delete_obj(_id):
    carousel.remove({'_id': _id})
    return True
