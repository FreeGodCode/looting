# -*- coding: utf8 -*-

import sys
import time
from datetime import datetime

from asynctools.threading import Async

from conf import conf_ver
from libs.db import (integer_red_subscribe)
from libs.utils import (push_template, unix_time_to_string)

# reload(sys)
# sys.setdefaultencoding('utf-8')


@Async
def start_push_template(integer_red_subscribe_obj, template_id):
    wx_uid = integer_red_subscribe_obj.get('wx_uid')
    created_time = integer_red_subscribe_obj.get('created_time')
    # start_time = 60 - int(datetime.now().strftime(format='%M'))
    start_time = 60 - int(datetime.now().strftime('%M'))
    push_template(wx_uid, template_id, '', '', created_time,
                  u'整点红包将于{0}分钟之后开始，请及时进入App参与活动，过期将无法获得奖金。'.format(start_time))
    integer_red_subscribe.update_one({'_id': integer_red_subscribe_obj.get('_id')}, {'$set': {'status': 1}})


def start_integer_red_subscribe():
    today_str_next = unix_time_to_string(unix_time=int(time.time()) + 60 * 60, format='%Y-%m-%d')
    hour_int_next = unix_time_to_string(unix_time=int(time.time()) + 60 * 60, format='%H')

    integer_red_subscribe_cur = integer_red_subscribe.find({'today_str': today_str_next, 'hour_int': hour_int_next,
                                                            'status': 0})
    if conf_ver == 'conf.ProductionConfig':
        template_id = 'uYbaifuTdV5t3w-vXXibloAMV_ueYzHfY890RIXFHEI'
    else:
        template_id = 'HOnVZPwa-cf9JCr5dzWNQA9QyoPZEexSsKU1YzQsQPY'
    for integer_red_subscribe_obj in integer_red_subscribe_cur:
        start_push_template(integer_red_subscribe_obj, template_id)
    time.sleep(10 * 60)

if __name__ == '__main__':
    start_integer_red_subscribe()
    # push_template('oOVUCvwftNal7rPFXr8vhIdF44YA', 'HOnVZPwa-cf9JCr5dzWNQA9QyoPZEexSsKU1YzQsQPY', '', '',
    #               datetime.now().strftime(format='%Y-%m-%d %H:%M:%S'),
    #               u'整点红包将于{0}分钟之后开始，请及时进入App参与活动，过期将无法获得奖金。'.format(1))
    # push_template('oOVUCvwftNal7rPFXr8vhIdF44YA', 'WgNk3x4EYRwMz853p-vl9TPxRS6GRGzEqjpN7aIcbD0', 12, u'John', u'12元',
    #               '')
