# -*- coding: utf8 -*-

from libs.common import get_datetime_str
from libs.db import configs, CONFIG_TYPE_APP_ROUTE
from libs.pymongo_ex import get_pageable


class Model:
    __TYPE = CONFIG_TYPE_APP_ROUTE

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'name': u'路由名称',
            'path': u'路由路径',
            'priority': u'优先度',
            'created_time': u'创建时间',
            'invalid': u'失效'
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'name': u'',
            'path': u'',
            'priority': 0,
            'created_time': get_datetime_str(),
            'invalid': 0
        }

    int_keys = ['priority', 'invalid']

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
