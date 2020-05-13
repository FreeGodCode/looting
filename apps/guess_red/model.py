# -*- coding: utf8 -*-

default_des = {
    'today_str': u'红包日期',
    'hour_int': u'发送小时点',
    'minute_int': u'发送分钟',
    'value': u'红包总金额(单位分)',
    'invalid_time': u'红包失效时间',
    'number_of_periods': u'第几期红包',
    'start_time': u'红包开始时间',
    'start_time_str': u'红包开始时间字符串',
    'status': u'红包状态',
    'nickname': u'用户昵称',
    'headimgurl': u'用户头像',
    'user_id': u'用户ID'
}
guess_red_detail_dict = {'nickname': u'用户昵称', 'headimgurl': u'用户头像', 'guess_time': u'猜的时间',
                         'status': u'猜的状态', 'guess_value': u'猜的值', 'number_of_periods': u'第几期',
                         'user_id': u'用户ID', 'millisecond': u'猜的毫秒', 'consume_calorific': u'消费的热量'}

default_values = {
    'today_str': u'',
    'hour_int': 0,
    'minute_int': 0,
    'number': 0,
    'status': 0
}

status_values = {
    -1: u'已过期',
    0: u'未猜中',
    1: u'已猜中',
}
int_key = ['hour_int', 'value', 'minute_int', 'status']
