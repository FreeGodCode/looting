# -*- coding: utf8 -*-

from libs.common import get_datetime_str
from libs.db import CONFIG_TYPE_INVITE_TASK, configs


class Model:
    __TYPE = CONFIG_TYPE_INVITE_TASK

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'status': u'状态',
            'reward_cash': u'奖励现金',
            'reward_coupon': u'奖励消耗卷',
            'created_time': u'创建时间',
            'rules':u'收益规则',
            'status_require_addnew':u'是否需要用户上新',
            'continue_check':u'用户连续签到天数',
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'status': 0,
            'reward_cash': 0.0,
            'reward_coupon': 0.0,
            'created_time': get_datetime_str(),
            'rules': u'',
            'status_require_addnew':1,
            'continue_check':3,
        }

    int_keys = ['status','status_require_addnew','continue_check']
    float_keys = ['reward_cash', 'reward_coupon']

    status_values = {
        0: u'关闭',
        1: u'开启'
    }

    def filter_criteria(self, criteria=None):
        if not criteria:
            criteria = {
                'type_num': self.__TYPE,
                'invalid': 0
            }
        else:
            criteria.update({
                'type_num': self.__TYPE,
                'invalid': 0
            })
        return criteria

    def get_detail_obj(self):
        detail_obj = configs.find_one(self.filter_criteria())
        if not detail_obj:
            detail_obj = model.default_values
        return detail_obj

    def update_obj(self, data):
        configs.update_one(self.filter_criteria(), {'$set': data}, upsert=True)
        return True


model = Model()
