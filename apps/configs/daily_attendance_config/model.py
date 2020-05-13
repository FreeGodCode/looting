# -*- coding: utf8 -*-

from libs.common import get_datetime_str
from libs.db import CONFIG_TYPE_DAILY_ATTENDANCE, configs
from libs.pymongo_ex import get_pageable


class Model:
    __TYPE = CONFIG_TYPE_DAILY_ATTENDANCE

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'serial_days': u'签到天数',
            'reward_value': u'奖励',
            'created_time': u'创建时间',
            'invalid': u'失效'
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'serial_days': 0,
            'reward_value': 0,
            'created_time': get_datetime_str(),
            'invalid': 0
        }

    int_keys = ['serial_days', 'reward_value']

    status_values = {
        0: u'关闭',
        1: u'开启'
    }

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
