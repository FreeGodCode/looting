# -*- coding: utf8 -*-
from libs.common import get_datetime_str
from libs.db import configs, CONFIG_TYPE_USER_LEVEL
from libs.pymongo_ex import get_pageable


class Model:
    __TYPE = CONFIG_TYPE_USER_LEVEL

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'name': u'等级名称',
            'level': u'用户等级',
            'icon_url': u'用户图像标识',
            'invite_num': u'邀请数量',
            'created_time': u'创建时间',
            'invalid': u'失效'
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'name': u'',
            'level': 0,
            'icon_url': u'',
            'invite_num': 0,
            'created_time': get_datetime_str(),
            'invalid': 0
        }

    int_keys = ['level', 'invite_num', 'invalid']

    @staticmethod
    def configs_info_processor(task_obj):
        return task_obj

    def filter_criteria(self, criteria):
        if not criteria:
            criteria = {
                'type_num': CONFIG_TYPE_USER_LEVEL,
                'invalid': 0
            }
        else:
            criteria.update({
                'type_num': CONFIG_TYPE_USER_LEVEL,
                'invalid': 0
            })
        return criteria

    def get_list_obj(self, criteria, page_num, limit):
        _cur = configs.find(self.filter_criteria(criteria))
        return get_pageable(_cur, page_num, limit, processor=self.configs_info_processor)

    def create_obj(self, data):
        result = configs.insert_one(data)

    def update_obj(self, _id, data):
        result = configs.update_one(self.filter_criteria({'_id': _id}), {'$set': data})

    def get_detail_obj(self, _id):
        detail_obj = configs.find_one(self.filter_criteria({'_id': _id}))
        return detail_obj

    def remove_obj(self, _id):
        configs.update_one(self.filter_criteria({'_id': _id}), {'$set': {'invalid': 1}})
        return True


model = Model()
