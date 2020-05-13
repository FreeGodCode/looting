# -*- coding: utf8 -*-
import time

from libs.db import daily_task, CONFIG_TYPE_TOP_TASK, configs
from libs.pymongo_ex import get_pageable
from libs.utils import timestamp_to_strftime


class _Model:
    @property
    def default_des(self):
        return {
            'name': u'任务名字',
            'reward_text': u'奖励描述',
            'img_url': u'任务图标',
            'task_type': u'任务类型',
            'event_id': u'触发事件id',
            'trigger_event_count': u'触发次数',
            'route_id': u'路由id',
            'next_step': u'',
            'start_time': u'任务开始时间',
            'end_time': u'任务结束时间',
            'reward_value': u'奖励消费卷',
            'status': u'状态',
            'sort_id': u'排序值',
            'remark': u'备注',
            'created_time': u'创建时间'
        }

    @property
    def default_values(self):
        return {
            'name': u'',
            'reward_text': u'',
            'img_url': u'',
            'task_type': u'daily_task',
            'event_id': u'触发事件id',
            'trigger_event_count': u'触发次数',
            'route_id': u'',
            'next_step': u'',
            'start_time': u'',
            'end_time': u'',
            'reward_value': 0,
            'sort_id': 0,
            'status': 0,
            'remark': u'',
            'created_time': timestamp_to_strftime(time.time())
        }

    @property
    def top_default_des(self):
        return {
            'top_task_name': u'顶级任务名称',
            'top_task_des': u'顶级任务描述',
            'reward_value': u'顶级任务奖励',
            'status': u'状态'
        }

    @property
    def top_default_values(self):
        return {
            'top_task_name': u'完成所有任务',
            'top_task_des': u'',
            'reward_value': 0,
            'status': 0
        }

    int_keys = ['sort_id', 'status', 'reward_value', 'trigger_event_count']

    top_int_keys = ['reward_value', 'status']

    status_values = {
        -1: u'隐藏',
        1: u'显示'
    }

    top_status_values = {
        -1: u'隐藏',
        1: u'显示'
    }


model = _Model()


def start_create_index():
    pass


def daily_task_info_processor(task_obj):
    task_obj['status_name'] = model.status_values.get(task_obj['status'])
    return task_obj


def get_list_obj(criteria, page_num, limit):
    _cur = daily_task.find(criteria)
    return get_pageable(_cur, page_num, limit, processor=daily_task_info_processor)


def create_obj(data):
    result = daily_task.insert_one(data)


def update_obj(_id, data):
    result = daily_task.update_one({'_id': _id}, {'$set': data})


def get_detail_obj(_id):
    detail_obj = daily_task.find_one({'_id': _id})
    return detail_obj


def delete_obj(_id):
    daily_task.remove({'_id': _id})
    return True


def update_top_task(update_data):
    configs.update({'type_num': CONFIG_TYPE_TOP_TASK}, {'$set': update_data}, upsert=True)
    return True


def get_top_task_detail():
    detail_obj = configs.find_one({'type_num': CONFIG_TYPE_TOP_TASK})
    if not detail_obj:
        return model.top_default_values
    return detail_obj
