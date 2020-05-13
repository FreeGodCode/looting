# -*- coding: utf8 -*-

from libs.common import get_datetime_str
from libs.db import task_event
from libs.pymongo_ex import get_pageable


class _Model:
    @property
    def default_des(self):
        return {
            'name': u'任务名字',
            'repeatable': u'是否可重入',
            'created_time': u'创建时间'
        }

    @property
    def default_values(self):
        return {
            'name': u'',
            'repeatable': 0,
            'created_time': get_datetime_str()
        }

    int_keys = []

    repeatable_values = {
        0: u'不可重复触发',
        1: u'可重复触发'
    }


model = _Model()


def start_create_index():
    pass


def task_event_info_processor(event_obj):
    return event_obj


def get_list_obj(criteria, page_num, limit):
    _cur = task_event.find(criteria)
    return get_pageable(_cur, page_num, limit, processor=task_event_info_processor)
