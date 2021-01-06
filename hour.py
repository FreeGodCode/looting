# -*- coding: utf-8 -*-
import json
import sys
import time
from datetime import datetime
from random import randint

import requests
from asynctools.threading import Async
from bson import ObjectId

from conf import conf_ver
from libs.common import red_envelopes_wechat, start_transfer_alipay
from libs.db import (req_log, redis_req_log, s_user_online_t, withdraw_record, user, operation, req_ip_statistical,
                     domain_h5)
from libs.utils import timestamp_to_strftime, jp_notification


# reload(sys)
# sys.setdefaultencoding('utf-8')


@Async
def async_inser_req(req_log_json):
    req_log.insert_one(req_log_json)


@Async
def async_ip_statistical(req_log_json):
    req_ip_user_num = len(s_user_online_t.find({'req_ip': req_log_json.get('req_ip', '')}).distinct('user_id'))
    req_ip_statistical.update_one({'req_ip': req_log_json.get('req_ip', '')},
                                  {'$set': {'req_ip_user_num': req_ip_user_num,
                                            'req_ip_area': req_log_json.get('req_ip_area', '')}}, upsert=True)


def insert_req_log():
    """
    插入正常请求日志
    :return:
    """
    hour_str = datetime.now().strftime(format='%H')
    while True:
        try:
            req_log_array = redis_req_log.brpop('req_log', timeout=2)
            if not req_log_array:
                new_hour_str = datetime.now().strftime(format='%H')
                if new_hour_str != hour_str:
                    break
                continue
            req_log_json = json.loads(req_log_array[1])
            async_inser_req(req_log_json)
            # 统计此用户的在线时长
            user_id = req_log_json.get('user_id')
            today = req_log_json.get('today')
            if user_id:
                user_obj = user.find_one({'_id': ObjectId(user_id)})
                # 更新用户的最新版本
                req_data = req_log_json.get('req_data')
                system_type = req_data.get('system_type')
                version_num = req_data.get('version_num')
                app_version = user_obj.get('app_version')

                if version_num > app_version:
                    user.update_one({'_id': ObjectId(user_id)},
                                    {'$set': {'app_version': version_num, 'mp_system_type': system_type}})

                req_time_stamp = req_log_json.get('time_stamp')
                s_user_online_t_obj = s_user_online_t.find_one({'user_id': user_id, 'today_str': today})
                if s_user_online_t_obj:
                    last_visit_time = s_user_online_t_obj.get('last_visit_time')
                    if last_visit_time == 0:
                        first_visit_time_h = timestamp_to_strftime(req_time_stamp, format='%H')
                        s_user_online_t.update_one({'_id': s_user_online_t_obj.get('_id')},
                                                   {'$set': {'length_visit_time': 0,
                                                             'first_visit_time': req_time_stamp,
                                                             'last_visit_time': req_time_stamp,
                                                             'req_ip': req_log_json.get('req_ip', ''),
                                                             'req_ip_area': req_log_json.get('req_ip_area', ''),
                                                             'first_visit_time_h': int(first_visit_time_h)}})
                    else:
                        length_visit_time = s_user_online_t_obj.get('length_visit_time')
                        time_interval = req_time_stamp - last_visit_time
                        if time_interval < 10 * 60:
                            length_visit_time += time_interval
                        s_user_online_t.update_one({'_id': s_user_online_t_obj.get('_id')},
                                                   {'$set': {'last_visit_time': req_time_stamp,
                                                             'length_visit_time': length_visit_time}})
                else:
                    first_visit_time_h = timestamp_to_strftime(req_time_stamp, format='%H')
                    try:
                        s_user_online_t.insert_one({'user_id': user_id, 'today_str': today,
                                                    'length_visit_time': 0,
                                                    'first_visit_time': req_time_stamp,
                                                    'last_visit_time': req_time_stamp,
                                                    'req_ip': req_log_json.get('req_ip', ''),
                                                    'req_ip_area': req_log_json.get('req_ip_area', ''),
                                                    'first_visit_time_h': int(first_visit_time_h),
                                                    'mp_system_type': user_obj.get('mp_system_type')})
                        async_ip_statistical(req_log_json)
                    except:
                        pass

                if user_obj:
                    today_str = datetime.now().strftime(format='%Y-%m-%d')
                    invite_active_status = user_obj.get('invite_active_status')
                    if invite_active_status == 1:
                        invite_active_time = user_obj.get('invite_active_time')
                        if invite_active_time != today_str:
                            user.update_one({'_id': ObjectId(user_id)}, {'$set': {'invite_active_status': 2}})
                    elif invite_active_status == 3:
                        invite_active_time = user_obj.get('invite_active_time')
                        if invite_active_time != today_str:
                            user.update_one({'_id': ObjectId(user_id)}, {'$set': {'invite_active_status': 4}})
            new_hour_str = datetime.now().strftime(format='%H')
            if new_hour_str != hour_str:
                break
        except:
            pass


def send_jg_notification():
    """
    整点发送app 通知
    :return:
    """
    if conf_ver == 'conf.ProductionConfig':
        hour_int = int(timestamp_to_strftime(time.time(), format='%H'))
        if hour_int in [12, 18]:
            title = u'热量星球'
            content = u'【热量星球】红包开抢了，你的朋友又抢了{0}.{1}元钱了，点击进入>>>'.format(randint(1, 5), randint(0, 5))
            alert = {
                'title': title,
                'body': content
            }
            try:
                jp_notification(alert, title, 'id', '')
            except:
                pass


def withdraw_record_search():
    """
    重新尝试 微信提现 发红包
    :return:
    """
    operation_obj = operation.find_one()
    automatic_withdraw_cash = operation_obj.get('automatic_withdraw_cash')
    withdraw_record_cur = withdraw_record.find(
        {'err_code': {'$ne': ''}, 'status': 0, 'origin': u'微信提现', 'value': {'$lt': automatic_withdraw_cash}})
    for withdraw_record_obj in withdraw_record_cur:
        red_envelopes_wechat(withdraw_record_obj)
        user_id = withdraw_record_obj.get('user_id', '')
        if withdraw_record.find_one({'user_id': user_id, 'status': 1}):
            withdraw_status = -1
        elif withdraw_record.find_one({'user_id': user_id, 'status': 0}):
            withdraw_status = 1
        elif withdraw_record.find_one({'user_id': user_id, 'status': -1}):
            withdraw_status = -2
        else:
            withdraw_status = 0
        user.update({'_id': ObjectId(user_id)}, {'$set': {'withdraw_status': withdraw_status}})


def withdraw_record_alipay():
    """
    重新尝试 支付宝提现转账
    :return:
    """
    operation_obj = operation.find_one()
    automatic_withdraw_cash = operation_obj.get('automatic_withdraw_cash')
    withdraw_record_cur = withdraw_record.find(
        {'err_code': {'$ne': ''}, 'status': 0, 'origin': u'支付宝提现', 'value': {'$lt': automatic_withdraw_cash}})
    for withdraw_record_obj in withdraw_record_cur:
        start_transfer_alipay(withdraw_record_obj)
        user_id = withdraw_record_obj.get('user_id', '')
        if withdraw_record.find_one({'user_id': user_id, 'status': 1}):
            withdraw_status = -1
        elif withdraw_record.find_one({'user_id': user_id, 'status': 0}):
            withdraw_status = 1
        elif withdraw_record.find_one({'user_id': user_id, 'status': -1}):
            withdraw_status = -2
        else:
            withdraw_status = 0
        user.update({'_id': ObjectId(user_id)}, {'$set': {'withdraw_status': withdraw_status}})


def check_domain():
    """
    检查邀请推广域名 状态
    :return:
    """
    check_url = 'http://106.52.180.177/api/realtime_watch/query'
    target_domain_h5_cur = domain_h5.find({'status': 1})
    for target_domain_h5_obj in target_domain_h5_cur:
        domain = target_domain_h5_obj.get('domain')
        is_invalid = False
        req = requests.post(check_url, data={'url': domain, 'type': 0})
        req_json = req.json()
        new_status = 0
        states = req_json.get('data', {}).get('states', [])
        for item in states:
            if item.get('state') == 2:
                if item.get('type') == 'icp':
                    new_status = -1
                is_invalid = True
                break
        if is_invalid:
            _target_domain_h5_obj = domain_h5.find_one({'status': 2})
            if _target_domain_h5_obj:
                domain_h5.update_one({'_id': _target_domain_h5_obj.get('_id')}, {'$set': {'status': 1}})
                domain_h5.update_one({'_id': target_domain_h5_obj.get('_id')}, {'$set': {'status': new_status}})
                domain_h5.update_many({}, {'$set': {'user_num': 0}})
            else:
                if domain_h5.find({'status': 1}).count() > 1:
                    domain_h5.update_one({'_id': target_domain_h5_obj.get('_id')}, {'$set': {'status': new_status}})


# 每小时执行一次的脚本
if __name__ == '__main__':
    try:
        # 整点发送app通知
        send_jg_notification()
    except:
        pass
    try:
        # 重新尝试 微信提现 发红包
        withdraw_record_search()
    except:
        pass
    try:
        # 重新尝试 支付宝提现
        withdraw_record_alipay()
    except:
        pass
    try:
        # 检查邀请推广域名 状态
        check_domain()
    except:
        pass
    try:
        # 插入正常请求日志
        insert_req_log()
    except Exception as e:
        print(str(e))
