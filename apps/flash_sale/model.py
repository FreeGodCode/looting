# -*- coding: utf8 -*-
import copy
from datetime import datetime

from asynctools.threading import Async

from libs.common import get_datetime_str
from libs.db import product, flash_sale_template, flash_sale, configs, CONFIG_TYPE_FLASH_SALE
from libs.pymongo_ex import get_pageable
from libs.utils import get_now_part


class _Model:
    @property
    def default_des(self):
        return {
            'product_id': u'商品id',
            'title': u'标题',
            'status': u'状态',
            'total_value': u'总分数',
            'cost_value': u'单次兑换消耗分数',
            'limit_num': u'总限制',
            'created_time': u'创建时间',
            'sort_num': u'排序值',
            'date_list': u'日期列表',
            'hour_list': u'小时列表',
            'notify': u'通知配置',
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
            'cost_value': 0,
            'limit_num': 0,
            'created_time': get_datetime_str(),
            'sort_num': 0,
            'date_list': [],
            'hour_list': [],
            'notify': [],
            'disabled': 0,
            'remark':u'',
            'rules': u''
        }

    int_keys = [
        'status',
        'total_value',
        'limit_num',
        'sort_num',
        'hour_list',
        'disabled'
    ]

    status_values = {
        0: u'下架',
        1: u'上架',
    }
    # status_values = {
    #     0: u'待开始',
    #     1: u'进行中',
    #     2: u'已结束',
    #     3: u'下架'
    # }


model = _Model()


def get_product_dict(product_id):
    product_obj = product.find_one({'_id': product_id})
    return product_obj


def flash_sale_template_info_processor(template_obj):
    product_obj = get_product_dict(template_obj['product_id'])
    product_obj.update(template_obj)
    if not product_obj['title']:
        product_obj['title'] = product_obj['name']
    try:
        product_obj['cost_count'] = product_obj['total_value'] / product_obj['cost_value']
    except:
        product_obj['cost_count'] = 0
    return product_obj


def flash_sale_info_processor(flash_sale_obj):
    _obj = flash_sale_template_info_processor(flash_sale_obj)
    date = _obj['date']
    hour = _obj['hour']
    end_hour = hour + 1 % 24
    _obj['hour_name'] = '%02d:00~%02d:00' % (hour, end_hour)
    _obj['date_name'] = get_datetime_str('%Y-%m-%d', date)
    return _obj

def get_list_obj(criteria, page_num, limit):
    criteria['disabled'] = 0
    _cur = flash_sale_template.find(criteria)
    return get_pageable(_cur, page_num, limit, processor=flash_sale_template_info_processor)


def get_real_list_obj(criteria, page_num, limit):
    _cur = flash_sale.find(criteria).sort([('date', 1), ('hour', 1)])
    return get_pageable(_cur, page_num, limit, processor=flash_sale_info_processor)


def create_obj(data, total_lottery_num, lottery_cost_value):
    data['total_value'] = total_lottery_num * lottery_cost_value
    data['cost_value'] = lottery_cost_value
    result = flash_sale_template.insert_one(data)
    sync_flash_sale(result.inserted_id)
    return True


def update_obj(_id, data, total_lottery_num, lottery_cost_value):
    data['total_value'] = total_lottery_num * lottery_cost_value
    data['cost_value'] = lottery_cost_value
    flash_sale_template.update_one({'_id': _id}, {'$set': data})
    sync_flash_sale(_id)
    return True


def get_detail_obj(_id):
    detail_obj = flash_sale_template.find_one({'_id': _id})
    detail_obj['total_lottery_num'] = detail_obj['total_value'] / detail_obj['cost_value']
    detail_obj['lottery_cost_value'] = detail_obj['cost_value']
    detail_obj['date_list'] = map(lambda x: x.strftime('%Y/%m/%d'), detail_obj['date_list'])
    return detail_obj


def delete_obj(_id):
    # 不允许从数据库删除，保持数据结构性
    flash_sale_template.update_one({'_id': _id}, {'$set': {'disabled': 1, 'status': 0}})
    return True


@Async
def sync_flash_sale(template_id):
    template_obj = flash_sale_template.find_one({'_id': template_id})
    if not template_obj:
        return
    if template_obj['status'] == 1:
        # 删除掉没有开始的任务
        flash_sale.remove({'template_id': template_id, 'status': 0})
        # 获取最大期号
        flash_sale_obj = flash_sale.find_one({'template_id': template_id, 'status': {'$ne': 0}},
                                             sort=[('issue_num', -1)])
        if not flash_sale_obj:
            issue_num = 1
        else:
            issue_num = flash_sale_obj['issue_num'] + 1
        date_list = template_obj['date_list']
        hour_list = template_obj['hour_list']
        now_date = get_now_part('%Y-%m-%d')
        for date in date_list:
            if date < now_date:
                continue
            elif date > now_date:
                is_today = False
            else:
                is_today = True
            for hour in hour_list:
                now_hour = datetime.now().hour
                if is_today and hour <= now_hour:
                    continue
                flash_sale_data = copy.copy(template_obj)
                if flash_sale_data.has_key('_id'):
                    del flash_sale_data['_id']
                if flash_sale_data.has_key('date_list'):
                    del flash_sale_data['date_list']
                if flash_sale_data.has_key('hour_list'):
                    del flash_sale_data['hour_list']
                if flash_sale_data.has_key('notify'):
                    del flash_sale_data['notify']
                flash_sale_data.update({
                    'template_id': template_obj['_id'],
                    'issue_num': issue_num,
                    'date': date,
                    'hour': hour,
                    'status': 0,
                    'cur_value': 0,
                    'pv_count': 0,
                    'play_count': 0,
                    'created_time': get_datetime_str()
                })
                flash_sale.insert_one(flash_sale_data)
                issue_num += 1
    else:
        # 删除掉没有开始的任务
        now = datetime.now()
        now_date = get_now_part('%Y-%m-%d')
        flash_sale.remove(
            {'template_id': template_id, 'status': 0, 'date': {'$gte': now_date}, 'hour': {'$gt': now.hour}})


def get_config_detail():
    config_obj = configs.find_one({'type_num': CONFIG_TYPE_FLASH_SALE})
    if not config_obj:
        config_obj = {'hour_list': list()}
    return config_obj


def update_config(data):
    configs.update_one({'type_num': CONFIG_TYPE_FLASH_SALE}, {'$set': data}, upsert=True)
