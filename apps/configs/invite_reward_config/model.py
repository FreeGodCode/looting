# -*- coding: utf8 -*-

from libs.common import get_datetime_str
from libs.db import configs, CONFIG_TYPE_INVITE_REWARD
from libs.pymongo_ex import get_pageable


class Model:
    __TYPE = CONFIG_TYPE_INVITE_REWARD

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'pile_num': u'邀请成绩',
            'worth_value': u'现金',
            'lottery_value': u'消耗卷',
            'threshold_invite_num': u'邀请人数阀值',
            'restricted_worth_value': u'受限现金',
            'restricted_lottery_value': u'受限消耗卷',
            'created_time': u'创建时间',
            'invalid': u'失效'
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'pile_num': 0,
            'worth_value': 0,
            'lottery_value': 0,
            'threshold_invite_num': 0,
            'restricted_worth_value': 0,
            'restricted_lottery_value': 0,
            'created_time': get_datetime_str(),
            'invalid': 0
        }

    int_keys = ['pile_num', 'threshold_invite_num', 'invalid']

    float_keys = ['lottery_value', 'worth_value', 'restricted_lottery_value', 'restricted_worth_value']

    @staticmethod
    def configs_info_processor(task_obj):
        return task_obj

    def filter_criteria(self, criteria):
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

    def get_list_obj(self, criteria, page_num, limit):
        _cur = configs.find(self.filter_criteria(criteria))
        return get_pageable(_cur, page_num, limit, processor=self.configs_info_processor)

    def create_obj(self, data):
        result = configs.insert_one(data)
        return True

    def update_obj(self, _id, data):
        result = configs.update_one(self.filter_criteria({'_id': _id}), {'$set': data})
        return True

    def get_detail_obj(self, _id):
        detail_obj = configs.find_one(self.filter_criteria({'_id': _id}))
        return detail_obj

    def remove_obj(self, _id):
        configs.update_one(self.filter_criteria({'_id': _id}), {'$set': {'invalid': 1}})
        return True

model = Model()
