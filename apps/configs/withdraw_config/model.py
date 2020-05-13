# -*- coding: utf8 -*-

from libs.common import get_datetime_str
from libs.db import configs, CONFIG_TYPE_WITHDRAW, CONFIG_TYPE_WITHDRAW_OPTION, CONFIG_TYPE_WITHDRAW_CLASS
from libs.pymongo_ex import get_pageable


class Model:
    __TYPE = CONFIG_TYPE_WITHDRAW

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'class_id': u'分类id',
            'value': u'金额',
            'status': u'状态',
            'invalid': u'无效'
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'class_id': u'',
            'value': 0,
            'status': 0,
            'invalid': 0
        }

    int_keys = ['value', 'status']
    status_value = {
        0: u'禁止',
        1: u'允许'
    }

    @staticmethod
    def configs_info_processor(withdraw_config_obj):
        class_id = withdraw_config_obj.get('class_id', None)
        class_name = u'无'
        if class_id:
            class_obj = class_model.get_detail_obj(class_id)
            class_name = class_obj['name']
        withdraw_config_obj['class_name'] = class_name
        return withdraw_config_obj

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

    def get_list_obj(self, criteria, page_num, limit):
        _cur = configs.find(self.filter_criteria(criteria))
        page_obj = get_pageable(_cur, page_num, limit, processor=self.configs_info_processor)
        return page_obj

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


class OptionModel:

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'service_charge': u'手续费',
            'is_rate': u'按比率计算',
            'enable_alipay': u'开启支付宝渠道',
            'enable_wechat_pay': u'开启微信支付渠道',
            'display_alipay': u'显示支付宝渠道',
            'display_wechat_pay': u'显示微信支付渠道'
        }

    @property
    def default_values(self):
        return {
            'type_num': CONFIG_TYPE_WITHDRAW_OPTION,
            'service_charge': 0,
            'is_rate': 0,
            'enable_alipay': 0,
            'enable_wechat_pay': 0,
            'display_alipay': 0,
            'display_wechat_pay': 0
        }

    int_keys = ['is_rate', 'enable_alipay', 'enable_wechat_pay', 'display_alipay', 'display_wechat_pay']
    switch_keys = ['enable_alipay', 'enable_wechat_pay', 'display_alipay', 'display_wechat_pay']
    float_keys = ['service_charge']

    def get_detail_obj(self):
        filter_dict = {
            'type_num': CONFIG_TYPE_WITHDRAW_OPTION
        }
        detail_obj = configs.find_one(filter_dict)
        if not detail_obj:
            detail_obj = option_model.default_values
        return detail_obj

    def update_obj(self, data):
        filter_dict = {
            'type_num': CONFIG_TYPE_WITHDRAW_OPTION
        }
        result = configs.update_one(filter_dict, {'$set': data}, upsert=True)


class ClassModel:
    __TYPE = CONFIG_TYPE_WITHDRAW_CLASS

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'name': u'分类名称',
            'limit_num': u'永久限制次数',
            'daily_limit_num': u'每日限制次数',
            'created_time': u'创建时间',
            'invalid': 0
        }

    @property
    def default_values(self):
        return {
            'type_num': self.__TYPE,
            'name': u'分类名称',
            'limit_num': 0,
            'daily_limit_num': 0,
            'created_time': get_datetime_str(),
            'invalid': 0
        }

    int_keys = ['limit', 'daily_limit']

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

    def get_list_obj(self, criteria, page_num, limit):
        _cur = configs.find(self.filter_criteria(criteria))
        page_obj = get_pageable(_cur, page_num, limit)
        return page_obj

    def get_detail_obj(self, _id):
        detail_obj = configs.find_one(self.filter_criteria({'_id': _id}))
        return detail_obj

    def create_obj(self, data):
        configs.insert_one(data)
        return True

    def update_obj(self, _id, data):
        configs.update_one({self.filter_criteria({'_id': _id})}, {'$set': data})
        return True

    def remove_obj(self, _id):
        configs.update_one({self.filter_criteria({'_id': _id})}, {'$set': {'invalid': 1}})
        return True


model = Model()
option_model = OptionModel()
class_model = ClassModel()
