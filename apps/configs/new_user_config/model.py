# -*- coding: utf8 -*-
from libs.common import get_datetime_str
from libs.db import configs, CONFIG_TYPE_NEW_USER


class Model:
    __TYPE = CONFIG_TYPE_NEW_USER

    @property
    def default_des(self):
        return {
            'type_num': u'配置类型',
            'status': u'状态',
            'reward_des': u'奖励描述',
            'coupon_reward_value': u'代金券奖励',
            'cash_reward_value': u'现金奖励',
            'created_time': u'创建时间'
        }

    @property
    def default_values(self):
        return {
            'type_num': CONFIG_TYPE_NEW_USER,
            'status': 0,
            'reward_des': u'新用户奖励',
            'coupon_reward_value': 0.0,
            'cash_reward_value': 0.0,
            'created_time': get_datetime_str()
        }

    int_keys = ['status']
    float_keys = ['coupon_reward_value', 'cash_reward_value']

    @staticmethod
    def configs_info_processor(new_user_config_obj):
        return new_user_config_obj

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

    def update_obj(self, _id, data):
        if not _id:
            configs.update_one({'type_num': self.__TYPE}, {'$set': data}, upsert=True)
        else:
            data['type_num'] = CONFIG_TYPE_NEW_USER
            result = configs.update_one({'_id': _id}, {'$set': data})
        return True

    def get_detail_obj(self):
        detail_obj = configs.find_one({'type_num': self.__TYPE})
        if not detail_obj:
            detail_obj = model.default_values
        return self.configs_info_processor(detail_obj)


model = Model()
