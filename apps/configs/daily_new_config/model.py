# -*- coding: utf8 -*-

from libs.common import get_datetime_str
from libs.db import CONFIG_TYPE_DAILY_NEW, configs, CONFIG_TYPE_USER_LEVEL
from libs.pymongo_ex import get_pageable


class Model:
    __TYPE = CONFIG_TYPE_DAILY_NEW

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'level_id': u'等级id',
            'cost_limit_num': u'消费限制数',
            'created_time': u'创建时间',
            'invalid': u'失效'
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'level_id': u'',
            'cost_limit_num': 0,
            'created_time': get_datetime_str(),
            'invalid': 0
        }

    int_keys = ['cost_limit_num']

    @staticmethod
    def configs_info_processor(config_obj):
        level_id = config_obj['level_id']
        level_obj = configs.find_one({'_id': level_id, 'type_num': CONFIG_TYPE_USER_LEVEL})
        config_obj['level_name'] = level_obj['name']
        config_obj['level'] = level_obj['level']
        return config_obj

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
