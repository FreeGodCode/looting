# -*- coding: utf-8 -*-
import hashlib
import json
import sys
import time
import uuid
from datetime import datetime

import requests
from bson import ObjectId

from libs.db import (user, system, redis_code, task2_code_data, redis_task2_code, redis_invite_code, commission_record,
                     withdraw_record, operation, redis_admin, s_user_online_t)
from libs.utils import random_str, timestamp_to_strftime


# reload(sys)
# sys.setdefaultencoding('utf-8')


# @Async
def compute_planet_calorific_total(planet_id):
    print(planet_id)
    if not planet_id:
        return False
    calorific_total_dict = user.aggregate([
        {
            '$match': {'$or': [{'planet_id': planet_id}, {'superior_planet_id': planet_id},
                               {'upperlevel_planet_id': planet_id}]}
        },
        {
            '$group': {'_id': '', 'calorific_total': {'$sum': '$calorific_total'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(calorific_total_dict, dict):

            _calorific_total_dict = calorific_total_dict.get('result')[0]
            planet_calorific_total = int(_calorific_total_dict.get('calorific_total'))
        else:
            _calorific_total_dict = calorific_total_dict.next()
            planet_calorific_total = int(_calorific_total_dict.get('calorific_total'))
    except:
        planet_calorific_total = 0
    if planet_id == '88888888':
        system.update_one({}, {'$set': {'planet_calorific_total': planet_calorific_total}})
    else:
        user.update_one({'_id': ObjectId(planet_id)}, {'$set': {'planet_calorific_total': planet_calorific_total}})


def send_compute_planet_calorific_task():
    """
    发送计算星球总热量的任务
    :return:
    """
    compute_planet_calorific_total('88888888')
    user_cur = user.find({'planet_id': {'$ne': ''}})
    for user_obj in user_cur:
        planet_id = user_obj.get('planet_id', '')
        if planet_id:
            redis_code.lpush('compute_planet_calorific', planet_id)


def start_compute_planet_calorific_task():
    """
    开始计算每个星球 的总热量
    :return:
    """
    while True:
        req_planet_calorific = redis_code.brpop('compute_planet_calorific', timeout=2)
        if not req_planet_calorific:
            break
        planet_id = req_planet_calorific[1]
        compute_planet_calorific_total(planet_id)


def generate_task2_code():
    """
    生成 关注公众号 领取奖励的验证码
    :return:
    """
    if task2_code_data.find({'status': 0}).count() < 100000:
        for i in range(1000):
            task2_code = random_str(6).upper()
            task2_code_obj = task2_code_data.find_one({'code': task2_code})
            if not task2_code_obj:
                task2_code_data.insert_one({'code': task2_code, 'status': 0,
                                            'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})


def send_task2_code():
    """
     发送领取奖励验证码的任务
    :return:
    """
    task2_code_len = redis_task2_code.llen('task2_code')
    if task2_code_len < 10000:
        task2_code_data_cur = task2_code_data.find({'status': 0}).limit(100)
        for task2_code_data_obj in task2_code_data_cur:
            task2_code_data.update_one({'_id': task2_code_data_obj.get('_id')}, {'$set': {'status': 1}})
            redis_task2_code.lpush('task2_code', task2_code_data_obj.get('code'))


def start_task2_code():
    """
     生成 关注公众号 领取奖励的验证码 并发送任务
    :return:
    """
    hour_str = datetime.now().strftime(format='%H')
    while True:
        try:
            # 生成 关注公众号 领取奖励的验证码
            generate_task2_code()
        except Exception as e:
            print('generate_task2_code: ' + str(e))
        try:
            # 将关注公众号 领取奖励的验证码 发送到消息队列任务
            send_task2_code()
        except Exception as e:
            print('send_task2_code: ' + str(e))

        new_hour_str = datetime.now().strftime(format='%H')
        if new_hour_str != hour_str:
            break
        time.sleep(60)


def check_registration_reward():
    """
    检查邀请用户首次注册是否奖励
    :return:
    """
    if int(timestamp_to_strftime(int(time.time()), format='%H')) == 0:
        return False
    last_hour_str = timestamp_to_strftime((int(time.time()) - 60 * 60), format='%Y-%m-%d %H')
    user_cur = user.find({'created_time': {'$regex': last_hour_str}})
    for user_obj in user_cur:
        invite_id = user_obj.get('invite_id', '')
        user_id = str(user_obj.get('_id'))
        if ObjectId.is_valid(invite_id):
            if not commission_record.find_one({'origin': u'邀请用户首次注册', 'user_id': invite_id,
                                               'contributor_id': user_id}):
                redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 1, 'invite_id': invite_id,
                                                                   'user_id': user_id}))


def check_withdraw_reward():
    """
    检查邀请用户首次提现是否奖励
    :return:
    """
    if int(timestamp_to_strftime(int(time.time()), format='%H')) == 0:
        return False
    today_str = timestamp_to_strftime((int(time.time()) - 60 * 60), format='%Y-%m-%d')
    last_hour_str = timestamp_to_strftime((int(time.time()) - 60 * 60), format='%Y-%m-%d %H')
    withdraw_record_cur = withdraw_record.find({'review_time': {'$regex': last_hour_str}, 'status': 1})
    for withdraw_record_obj in withdraw_record_cur:
        user_id = withdraw_record_obj.get('user_id')
        user_obj = user.find_one({'_id': ObjectId(user_id)})
        invite_id = user_obj.get('invite_id', '')
        if ObjectId.is_valid(invite_id):
            if not commission_record.find_one({'origin': u'邀请用户首次提现', 'user_id': invite_id,
                                               'contributor_id': user_id}):
                _withdraw_record_obj = withdraw_record.find({'user_id': user_id,
                                                             'status': 1}).sort([('review_time', 1)])[0]

                first_time_today = _withdraw_record_obj.get('review_time').split(' ')[0]
                if first_time_today == today_str:
                    redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 2, 'invite_id': invite_id,
                                                                       'user_id': user_id}))


def third_transfer_profit():
    """
    统计第三方文章的有效阅读数
    :return:
    """
    today_str = timestamp_to_strftime(int(time.time()), format='%Y-%m-%d')
    operation_obj = operation.find_one()
    wechat_transfer_cash = int(operation_obj.get('wechat_transfer_cash', 20))
    wechat_transfer_per_deduction = int(operation_obj.get('wechat_transfer_per_deduction', 70))
    user_cur = user.find({'status': 0})
    for user_obj in user_cur:
        user_id = str(user_obj.get('_id'))
        third_transfer_art_token = user_obj.get('third_transfer_art_token')
        if third_transfer_art_token:
            redis_admin.lpush('third_transfer_profit_h',
                              json.dumps({'third_transfer_art_token': third_transfer_art_token,
                                          'user_id': user_id}))
    while True:
        try:
            third_transfer_profit_req = redis_admin.brpop('third_transfer_profit_h', timeout=2)
            if not third_transfer_profit_req:
                break
            third_transfer_profit_dict = json.loads(third_transfer_profit_req[1])
            user_id = third_transfer_profit_dict.get('user_id')
            third_transfer_art_token = third_transfer_profit_dict.get('third_transfer_art_token')
            json_data = {}
            for i in range(3):
                try:
                    ts = int(time.time() * 1000)
                    uuid_m = hashlib.md5(str(uuid.uuid4()).replace('-', ''))
                    opt = {'day': today_str, 'token': third_transfer_art_token,
                           'uuid': uuid_m.hexdigest(), 'ts': ts}
                    result = ''
                    key_az = sorted(opt.keys())
                    for k in key_az:
                        v = str(opt.get(k, '')).strip()
                        if not v:
                            continue
                        try:
                            v = v.encode('utf8')
                        except:
                            v = v.decode("ascii").encode('utf8')
                        result += v
                    result = result + '1234567890VGY&XDR%'
                    m = hashlib.md5(result)
                    md5_text = m.hexdigest()
                    resp = requests.post('https://api.5qx8.cn/api/open-fetch-user-data',
                                         headers={'sign': md5_text,
                                                  'Content-Type': 'multipart/form-data'}, params=opt)
                    req_json = resp.json()
                    if req_json.get('code') == 0 and req_json.get('data', {}):
                        json_data = req_json.get('data', {})
                        break
                except Exception as e:
                    print(e)
                    continue
            if json_data:
                ips = json_data.get('ips', 0)
                if ips:
                    real_ips = ips - int(wechat_transfer_per_deduction * ips / 100)
                    real_value = wechat_transfer_cash * real_ips
                    s_user_online_t.update_one({'today_str': today_str, 'user_id': user_id},
                                               {'$set': {'show_wechat_transfer_ips': real_ips,
                                                         'show_cash': real_value}})
        except:
            pass


# 每小时执行一次的脚本
if __name__ == '__main__':
    try:
        # 检查邀请用户首次提现是否奖励
        check_withdraw_reward()
    except Exception as e:
        print(str(e))
    try:
        # 检查邀请用户首次注册是否奖励
        check_registration_reward()
    except Exception as e:
        print(str(e))
    try:
        # 发送计算星球总热量的任务
        send_compute_planet_calorific_task()
    except Exception as e:
        print(str(e))
    try:
        # 开始计算每个星球 的总热量
        start_compute_planet_calorific_task()
    except Exception as e:
        print(str(e))
    try:
        # 生成 关注公众号 领取奖励的验证码 并发送任务
        start_task2_code()
    except Exception as e:
        print('start_task2_code: ' + str(e))
    try:
        third_transfer_profit()
    except:
        pass
