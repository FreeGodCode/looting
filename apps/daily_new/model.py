# -*- coding: utf8 -*-
from datetime import datetime

from asynctools.threading import Async

from libs.common import get_datetime_str
from libs.db import daily_new_template, product, daily_new
from libs.pymongo_ex import get_pageable
from libs.utils import get_now_part


class _Model:
    int_keys = ['status', 'total_value', 'cur_value', 'single_limit_num', 'limit_num', 'cost_value', 'sort_num',
                'pv_count', 'play_count', 'auto_result', 'auto_putaway', 'disabled']

    status_values = {
        0: u'下架',
        1: u'上架',
    }

    str_bool_keys = ['auto_result', 'auto_putaway', 'notify']

    @property
    def default_des(self):
        return {
            'product_id': u'商品id',
            'title': u'标题',
            'status': u'状态',
            'total_value': u'总奖券数',
            'single_limit_num': u'单次消费次数',
            'limit_num': u'总消费次数',
            'cost_value': u'购买消耗数',
            'created_time': u'创建时间',
            'sort_num': u'排序值',
            'auto_result': u'自动开奖',
            'auto_putaway': u'自动上架',
            'notify': u'通知选项',
            'disabled': u'禁止',
            'remark':u'备注',
            'rules':u'玩法规则',
        }

    @property
    def default_values(self):
        return {
            'product_id': u'',
            'title': u'',
            'status': 0,
            'total_value': 0,
            'single_limit_num': 0,
            'limit_num': 0,
            'cost_value': 0,
            'created_time': get_datetime_str(),
            'sort_num': 0,
            'auto_result': 0,
            'auto_putaway': 0,
            'notify': {},
            'disabled': 0,
            'remark':u'',
            'rules':u'',
        }

    auto_result_values = {
        0: '手动开奖',
        1: '自动开奖'
    }
    auto_putaway_values = {
        0: '手动上架',
        1: '自动上架'
    }


model = _Model()


def get_product_dict(product_id):
    product_obj = product.find_one({'_id': product_id})
    return product_obj


def daily_new_template_info_processor(template_obj):
    product_obj = get_product_dict(template_obj['product_id'])
    product_obj.update(template_obj)

    try:
        product_obj['cost_count'] = product_obj['total_value'] / product_obj['cost_value']
    except:
        product_obj['cost_count'] = 0

    if not product_obj.has_key('title'):
        product_obj['title'] = product_obj['name']

    product_obj['auto_result_name'] = model.auto_result_values.get(product_obj['auto_result'])
    product_obj['auto_putaway_name'] = model.auto_putaway_values.get(product_obj['auto_putaway'])
    return product_obj


def get_list_obj(criteria, page_num, limit):
    criteria['disabled'] = 0
    _cur = daily_new_template.find(criteria)
    return get_pageable(_cur, page_num, limit, processor=daily_new_template_info_processor)


def create_obj(data, total_lottery_num, lottery_cost_value):
    data['total_value'] = total_lottery_num * lottery_cost_value
    data['cost_value'] = lottery_cost_value
    result = daily_new_template.insert_one(data)
    sync_daily_new(result.inserted_id)


def update_obj(_id, data, total_lottery_num, lottery_cost_value):
    data['total_value'] = total_lottery_num * lottery_cost_value
    data['cost_value'] = lottery_cost_value
    result = daily_new_template.update_one({'_id': _id}, {'$set': data})
    sync_daily_new(_id)


def get_detail_obj(_id):
    detail_obj = daily_new_template.find_one({'_id': _id})
    detail_obj['total_lottery_num'] = detail_obj['total_value'] / detail_obj['cost_value']
    detail_obj['lottery_cost_value'] = detail_obj['cost_value']
    return detail_obj


def delete_obj(_id):
    # 不允许从数据库删除，保持数据结构性
    daily_new_template.update_one({'_id': _id}, {'$set': {'disabled': 1, 'status': 0}})
    return True


def merge(template_obj, daily_new_obj):
    issue_num = 1
    if daily_new_obj:
        issue_num = daily_new_obj['issue_num'] + 1
    else:
        daily_new_obj = dict()
    daily_new_obj.update({
        'product_id': template_obj['product_id'],
        'issue_num': issue_num,
        'title': template_obj['title'],
        'total_value': template_obj['total_value'],
        'cur_value': 0,
        'single_limit_num': template_obj['single_limit_num'],
        'limit_num': template_obj['limit_num'],
        'cost_value': template_obj['cost_value'],
        'created_time': get_datetime_str(),
        'sort_num': template_obj['sort_num'],
        'template_id': template_obj['_id'],
        'auto_result': template_obj['auto_result'],
        'auto_putaway': template_obj['auto_putaway'],
        'status': 0,
        'pv_count': 0,
        'play_count': 0,
    })
    return daily_new_obj


@Async
def sync_daily_new(template_id):
    template_obj = daily_new_template.find_one({'_id': template_id})
    if not template_obj:
        return
    if template_obj['status'] == 1:
        daily_new_obj = daily_new.find_one({'template_id': template_id, 'status': 0})
        if daily_new_obj:
            cur_value = daily_new_obj['cur_value']
            if cur_value == 0:
                daily_new_obj = merge(template_obj, daily_new_obj)
                # 没有任何参与的每日上新允许更新
                daily_new.update_one({'_id': daily_new_obj['_id'], 'cur_value': 0}, {'$set': daily_new_obj})
        else:
            daily_new_obj = daily_new.find_one({'template_id': template_id, 'status': 2}, sort=[('issue_num', -1)])
            daily_new_obj = merge(template_obj, daily_new_obj)
            # 没有正在进行中的每日上新，添加新的每日上新
            try:
                daily_new.insert_one(daily_new_obj)
            except:
                pass
    else:
        # 只允许下架没有任何人参与的每日上新
        # 防止脚本出错，删掉以前记录
        now = datetime.now()
        now_date = get_now_part('%Y-%m-%d')
        daily_new.delete_one(
            {'template_id': template_id, 'status': 0, 'date': {'$gte': now_date}, 'hour': {'$gt': now.hour}})


def get_real_list_obj(criteria, page_num, limit):
    _cur = daily_new.find(criteria)
    return get_pageable(_cur, page_num, limit, processor=daily_new_template_info_processor)
