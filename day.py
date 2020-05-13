# -*- coding: utf8 -*-
import hashlib
import json
import sys
import time
import uuid
from datetime import datetime

import requests
from bson import ObjectId

from libs.db import (statistical_day, user, commission_record, reg_user, calorific_record, red_record, withdraw_record,
                     s_user_online_t, req_log, deviant_log, error_log, system, earth_code, leaderboard, redis_code,
                     user_offline_pullup, ad_statistical_day, leaderboard_withdraw, statistical_day_official, operation,
                     redis_admin, redis_invite_code, integer_red_detail, guess_red_detail)
from libs.utils import timestamp_to_strftime, jp_notification, send_sms_163, get_chars2

reload(sys)
sys.setdefaultencoding('utf-8')


class Inviter_recursiver():
    def __init__(self):
        self.total = 0

    def calculate_inviter_recursiver(self, invite_id, today_str=''):
        if today_str:
            user_cur = user.find({'invite_id': invite_id, 'created_time': {'$regex': today_str}})
        else:
            user_cur = user.find({'invite_id': invite_id})
        for user_obj in user_cur:
            self.total += 1
            self.calculate_inviter_recursiver(str(user_obj.get('_id')), today_str)


def generate_statistical_day(yesterday_str=timestamp_to_strftime((int(time.time()) - 24 * 60 * 60), format='%Y-%m-%d')):
    """
    生成昨天 报表数据
    :return:
    """
    earth_code_list = earth_code.find({}).distinct('invite_code')
    earth_code_list.append('')
    user_num_invite = user.find({'created_time': {'$regex': yesterday_str},
                                 'invite_id': {'$nin': earth_code_list}, }).count()
    red_record_num = red_record.find({'today': yesterday_str, 'type_num': {'$in': [2, 3]}}).count()
    user_red_record = len(red_record.find({'today': yesterday_str}).distinct('user_id'))
    red_average_num = '%.2f' % (float(red_record_num) / float(user_red_record))

    planet_commission_dict = commission_record.aggregate([
        {
            '$match': {'today': yesterday_str}
        },
        {
            '$group': {'_id': '', 'planet_commission': {'$sum': '$value'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(planet_commission_dict, dict):

            _planet_commission_dict = planet_commission_dict.get('result')[0]
            planet_commission = int(_planet_commission_dict.get('planet_commission'))
        else:
            _planet_commission_dict = planet_commission_dict.next()
            planet_commission = int(_planet_commission_dict.get('planet_commission'))
    except:
        planet_commission = 0
    planet_commission_total = system.find_one().get('planet_commission_total', 0)
    planet_commission_total_dict = user.aggregate([
        {
            '$match': {'grade': 1}
        },
        {
            '$group': {'_id': '', 'planet_commission_total': {'$sum': '$planet_commission_total'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(planet_commission_total_dict, dict):

            _planet_commission_total_dict = planet_commission_total_dict.get('result')[0]
            planet_commission_total += int(_planet_commission_total_dict.get('planet_commission_total'))
        else:
            _planet_commission_total_dict = planet_commission_total_dict.next()
            planet_commission_total += int(_planet_commission_total_dict.get('planet_commission_total'))
    except:
        pass
    calorific_total_dict = calorific_record.aggregate([
        {
            '$match': {'today': yesterday_str, 'symbol': 1}
        },
        {
            '$group': {'_id': '', 'calorific_total': {'$sum': '$value'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(calorific_total_dict, dict):

            _calorific_total_dict = calorific_total_dict.get('result')[0]
            calorific_num_obtain = int(_calorific_total_dict.get('calorific_total'))
        else:
            _calorific_total_dict = calorific_total_dict.next()
            calorific_num_obtain = int(_calorific_total_dict.get('calorific_total'))
    except:
        calorific_num_obtain = 0

    calorific_total_dict = calorific_record.aggregate([
        {
            '$match': {'today': yesterday_str, 'symbol': -1}
        },
        {
            '$group': {'_id': '', 'calorific_total': {'$sum': '$value'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(calorific_total_dict, dict):

            _calorific_total_dict = calorific_total_dict.get('result')[0]
            calorific_num_expend = int(_calorific_total_dict.get('calorific_total'))
        else:
            _calorific_total_dict = calorific_total_dict.next()
            calorific_num_expend = int(_calorific_total_dict.get('calorific_total'))
    except:
        calorific_num_expend = 0
    calorific_num_dict = user.aggregate([
        {
            '$match': {}
        },
        {
            '$group': {'_id': '', 'available_calorific_num': {'$sum': '$available_calorific'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(calorific_num_dict, dict):

            _calorific_num_dict = calorific_num_dict.get('result')[0]
            calorific_num = int(_calorific_num_dict.get('available_calorific_num'))
        else:
            _calorific_num_dict = calorific_num_dict.next()
            calorific_num = int(_calorific_num_dict.get('available_calorific_num'))
    except:
        calorific_num = 0
    red_num_dict = red_record.aggregate([
        {
            '$match': {'today': yesterday_str}
        },
        {
            '$group': {'_id': '', 'red_num_total': {'$sum': '$value'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(red_num_dict, dict):

            _red_num_dict = red_num_dict.get('result')[0]
            red_num = int(_red_num_dict.get('red_num_total'))
        else:
            _red_num_dict = red_num_dict.next()
            red_num = int(_red_num_dict.get('red_num_total'))
    except:
        red_num = 0

    user_balance_dict = user.aggregate([
        {
            '$match': {}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_total = 0

    withdraw_total_dict = withdraw_record.aggregate([
        {
            '$match': {'today': yesterday_str, 'status': {'$ne': -1}}
        },
        {
            '$group': {'_id': '', 'withdraw_total': {'$sum': '$value'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(withdraw_total_dict, dict):

            _withdraw_total_dict = withdraw_total_dict.get('result')[0]
            withdraw_total = int(_withdraw_total_dict.get('withdraw_total'))
        else:
            _withdraw_total_dict = withdraw_total_dict.next()
            withdraw_total = int(_withdraw_total_dict.get('withdraw_total'))
    except:
        withdraw_total = 0
    integer_red_user_id_list = integer_red_detail.find({'today_str': yesterday_str}).distinct('user_id')
    integer_red_user_num = len(integer_red_user_id_list)
    guess_red_user_id_list = guess_red_detail.find({'guess_time': {'$regex': yesterday_str}}).distinct('user_id')
    guess_red_user_num = len(guess_red_user_id_list)
    statistical_day.insert_one({
        'today_str': yesterday_str,
        'planet_num': user.find({'planet_id': {'$ne': ''}}).count(),
        'planet_commission': planet_commission,
        'planet_commission_total': planet_commission_total,
        'user_num_total': user.find({}).count(),
        'user_num': user.find({'created_time': {'$regex': yesterday_str}}).count(),
        'user_num_novice_task': user.find({'created_time': {'$regex': yesterday_str}, 'new_value': -1}).count(),
        'user_num_invite': user_num_invite,
        'red_record_num': red_record_num,
        'user_red_record': user_red_record,
        'red_average_num': red_average_num,
        'user_num_invite_bind': reg_user.find({'today': yesterday_str, 'is_bind': 1}).count(),
        'user_num_active': s_user_online_t.find({'today_str': yesterday_str}).count(),
        'calorific_num_obtain': calorific_num_obtain,
        'calorific_num_expend': calorific_num_expend,
        'calorific_num': calorific_num,
        'red_num': red_num,
        'user_balance_num': balance_total,
        'withdraw_num': withdraw_total,
        'integer_red_user_num': integer_red_user_num,
        'guess_red_user_num': guess_red_user_num
    })


def generate_ad_statistical_day(
        yesterday_str=timestamp_to_strftime((int(time.time()) - 24 * 60 * 60), format='%Y-%m-%d')):
    """
    生成昨天 广告统计数据
    :return:
    """

    ad_total_dict = s_user_online_t.aggregate([
        {
            '$match': {'today_str': yesterday_str}
        },
        {
            '$group': {'_id': '', 'video_num_total': {'$sum': '$video_num'},
                       'video_num_total1': {'$sum': '$video_num1'},
                       'video_num_total2': {'$sum': '$video_num2'}, 'video_num_total3': {'$sum': '$video_num3'},
                       'video_num_total4': {'$sum': '$video_num4'}, 'home_ad_total1': {'$sum': '$home_ad1'},
                       'home_ad_total2': {'$sum': '$home_ad2'}, 'home_ad_total3': {'$sum': '$home_ad3'},
                       'home_ad_total4': {'$sum': '$home_ad4'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(ad_total_dict, dict):

            _ad_total_dict = ad_total_dict.get('result')[0]

            video_num_total = int(_ad_total_dict.get('video_num_total'))
            video_num_total1 = int(_ad_total_dict.get('video_num_total1'))
            video_num_total2 = int(_ad_total_dict.get('video_num_total2'))
            video_num_total3 = int(_ad_total_dict.get('video_num_total3'))
            video_num_total4 = int(_ad_total_dict.get('video_num_total4'))
            home_ad_total1 = int(_ad_total_dict.get('home_ad_total1'))
            home_ad_total2 = int(_ad_total_dict.get('home_ad_total2'))
            home_ad_total3 = int(_ad_total_dict.get('home_ad_total3'))
            home_ad_total4 = int(_ad_total_dict.get('home_ad_total4'))
        else:
            _ad_total_dict = ad_total_dict.next()

            video_num_total = int(_ad_total_dict.get('video_num_total'))
            video_num_total1 = int(_ad_total_dict.get('video_num_total1'))
            video_num_total2 = int(_ad_total_dict.get('video_num_total2'))
            video_num_total3 = int(_ad_total_dict.get('video_num_total3'))
            video_num_total4 = int(_ad_total_dict.get('video_num_total4'))
            home_ad_total1 = int(_ad_total_dict.get('home_ad_total1'))
            home_ad_total2 = int(_ad_total_dict.get('home_ad_total2'))
            home_ad_total3 = int(_ad_total_dict.get('home_ad_total3'))
            home_ad_total4 = int(_ad_total_dict.get('home_ad_total4'))
    except Exception, e:
        print e
        video_num_total = 0
        video_num_total1 = 0
        video_num_total2 = 0
        video_num_total3 = 0
        video_num_total4 = 0
        home_ad_total1 = 0
        home_ad_total2 = 0
        home_ad_total3 = 0
        home_ad_total4 = 0
    video_user_num = s_user_online_t.find({'today_str': yesterday_str, 'video_num': {'$gt': 0}}).count()
    video_user_num1 = s_user_online_t.find({'today_str': yesterday_str, 'video_num1': {'$gt': 0}}).count()
    video_user_num2 = s_user_online_t.find({'today_str': yesterday_str, 'video_num2': {'$gt': 0}}).count()
    video_user_num3 = s_user_online_t.find({'today_str': yesterday_str, 'video_num3': {'$gt': 0}}).count()
    video_user_num4 = s_user_online_t.find({'today_str': yesterday_str, 'video_num4': {'$gt': 0}}).count()
    video_user_num_total = s_user_online_t.find({'today_str': yesterday_str,
                                                 '$or': [{'video_num': {'$gt': 0}}, {'video_num1': {'$gt': 0}},
                                                         {'video_num2': {'$gt': 0}}, {'video_num3': {'$gt': 0}},
                                                         {'video_num4': {'$gt': 0}}]}).count()

    video_num_total_all = video_num_total + video_num_total1 + video_num_total2 + video_num_total3 + video_num_total4
    video_user_num_average = 0
    video_user_num_average1 = 0
    video_user_num_average2 = 0
    video_user_num_average3 = 0
    video_user_num_average4 = 0
    video_user_num_average_all = 0
    if video_user_num > 0:
        video_user_num_average = float('%.2f' % (float(video_num_total) / float(video_user_num)))
    if video_user_num1 > 0:
        video_user_num_average1 = float('%.2f' % (float(video_num_total1) / float(video_user_num1)))
    if video_user_num2:
        video_user_num_average2 = float('%.2f' % (float(video_num_total2) / float(video_user_num2)))
    if video_user_num3:
        video_user_num_average3 = float('%.2f' % (float(video_num_total3) / float(video_user_num3)))
    if video_user_num4:
        video_user_num_average4 = float('%.2f' % (float(video_num_total4) / float(video_user_num4)))
    if video_user_num_total:
        video_user_num_average_all = float('%.2f' % (float(video_num_total_all) / float(video_user_num_total)))

    home_ad_user_num1 = s_user_online_t.find({'today_str': yesterday_str, 'home_ad1': {'$gt': 0}}).count()
    home_ad_user_num2 = s_user_online_t.find({'today_str': yesterday_str, 'home_ad2': {'$gt': 0}}).count()
    home_ad_user_num3 = s_user_online_t.find({'today_str': yesterday_str, 'home_ad3': {'$gt': 0}}).count()
    home_ad_user_num4 = s_user_online_t.find({'today_str': yesterday_str, 'home_ad4': {'$gt': 0}}).count()

    home_ad_user_num_total = s_user_online_t.find({'today_str': yesterday_str,
                                                   '$or': [{'home_ad1': {'$gt': 0}}, {'home_ad2': {'$gt': 0}},
                                                           {'home_ad3': {'$gt': 0}}, {'home_ad4': {'$gt': 0}}]}).count()
    home_ad_total_all = home_ad_total1 + home_ad_total2 + home_ad_total3 + home_ad_total4

    home_ad_user_num_average1 = 0
    home_ad_user_num_average2 = 0
    home_ad_user_num_average3 = 0
    home_ad_user_num_average4 = 0
    home_ad_user_num_average_all = 0
    if home_ad_user_num1 > 0:
        home_ad_user_num_average1 = float('%.2f' % (float(home_ad_total1) / float(home_ad_user_num1)))
    if home_ad_user_num2 > 0:
        home_ad_user_num_average2 = float('%.2f' % (float(home_ad_total2) / float(home_ad_user_num2)))
    if home_ad_user_num3:
        home_ad_user_num_average3 = float('%.2f' % (float(home_ad_total3) / float(home_ad_user_num3)))
    if home_ad_user_num4:
        home_ad_user_num_average4 = float('%.2f' % (float(home_ad_total4) / float(home_ad_user_num4)))
    if home_ad_user_num_total:
        home_ad_user_num_average_all = float('%.2f' % (float(home_ad_total_all) / float(home_ad_user_num_total)))

    ad_statistical_day.update_one({'today_str': yesterday_str}, {'$set': {
        'today_str': yesterday_str,
        'video_num_total': video_num_total,
        'video_num_total1': video_num_total1,
        'video_num_total2': video_num_total2,
        'video_num_total3': video_num_total3,
        'video_num_total4': video_num_total4,
        'video_num_total_all': video_num_total_all,
        'video_user_num': video_user_num,
        'video_user_num1': video_user_num1,
        'video_user_num2': video_user_num2,
        'video_user_num3': video_user_num3,
        'video_user_num4': video_user_num4,
        'video_user_num_total': video_user_num_total,
        'video_user_num_average': video_user_num_average,
        'video_user_num_average1': video_user_num_average1,
        'video_user_num_average2': video_user_num_average2,
        'video_user_num_average3': video_user_num_average3,
        'video_user_num_average4': video_user_num_average4,
        'video_user_num_average_all': video_user_num_average_all,

        'home_ad_total1': home_ad_total1,
        'home_ad_total2': home_ad_total2,
        'home_ad_total3': home_ad_total3,
        'home_ad_total4': home_ad_total4,
        'home_ad_total_all': home_ad_total_all,
        'home_ad_user_num1': home_ad_user_num1,
        'home_ad_user_num2': home_ad_user_num2,
        'home_ad_user_num3': home_ad_user_num3,
        'home_ad_user_num4': home_ad_user_num4,
        'home_ad_user_num_total': home_ad_user_num_total,
        'home_ad_user_num_average1': home_ad_user_num_average1,
        'home_ad_user_num_average2': home_ad_user_num_average2,
        'home_ad_user_num_average3': home_ad_user_num_average3,
        'home_ad_user_num_average4': home_ad_user_num_average4,
        'home_ad_user_num_average_all': home_ad_user_num_average_all
    }}, upsert=True)


def generate_statistical_retain():
    for i in range(1, 31):
        today_str = timestamp_to_strftime((int(time.time()) - i * 24 * 60 * 60), format='%Y-%m-%d')
        today_str1 = timestamp_to_strftime((int(time.time()) - (i - 1) * 24 * 60 * 60), format='%Y-%m-%d')
        today_str2 = timestamp_to_strftime((int(time.time()) - (i - 2) * 24 * 60 * 60), format='%Y-%m-%d')
        today_str3 = timestamp_to_strftime((int(time.time()) - (i - 3) * 24 * 60 * 60), format='%Y-%m-%d')
        today_str7 = timestamp_to_strftime((int(time.time()) - (i - 7) * 24 * 60 * 60), format='%Y-%m-%d')
        today_str30 = timestamp_to_strftime((int(time.time()) - (i - 30) * 24 * 60 * 60), format='%Y-%m-%d')
        user_total = user.find({'created_time': {'$regex': today_str}}).count()
        user_id_list = []
        user_cur = user.find({'created_time': {'$regex': today_str}})
        for user_obj in user_cur:
            user_id_list.append((str(user_obj.get('_id'))))
        user_num_1 = s_user_online_t.find({'today_str': today_str1, 'user_id': {'$in': user_id_list}}).count()
        user_num_2 = s_user_online_t.find({'today_str': today_str2, 'user_id': {'$in': user_id_list}}).count()
        user_num_3 = s_user_online_t.find({'today_str': today_str3, 'user_id': {'$in': user_id_list}}).count()
        user_num_7 = s_user_online_t.find({'today_str': today_str7, 'user_id': {'$in': user_id_list}}).count()
        user_num_30 = s_user_online_t.find({'today_str': today_str30, 'user_id': {'$in': user_id_list}}).count()
        user_1_per = '%.2f' % (float(user_num_1 * 100) / float(user_total)) + '%'
        user_2_per = '%.2f' % (float(user_num_2 * 100) / float(user_total)) + '%'
        user_3_per = '%.2f' % (float(user_num_3 * 100) / float(user_total)) + '%'
        user_7_per = '%.2f' % (float(user_num_7 * 100) / float(user_total)) + '%'
        user_30_per = '%.2f' % (float(user_num_30 * 100) / float(user_total)) + '%'
        statistical_day.update_one({'today_str': today_str},
                                   {'$set': {'user_1_per': user_1_per, 'user_2_per': user_2_per,
                                             'user_3_per': user_3_per, 'user_7_per': user_7_per,
                                             'user_30_per': user_30_per}})


def strat_ad_statistical_day():
    for i in range(1, 31):
        today_str = timestamp_to_strftime((int(time.time()) - i * 24 * 60 * 60), format='%Y-%m-%d')
        generate_ad_statistical_day(today_str)


def delete_user_online_data():
    """
    删除用户在线时长 一个月前的
    :return:
    """
    m_str = timestamp_to_strftime((int(time.time()) - 31 * 24 * 60 * 60), format='%Y-%m-%d')
    s_user_online_t.remove({'today_str': {'$lt': m_str}})
    d_str = timestamp_to_strftime((int(time.time()) - 7 * 24 * 60 * 60), format='%Y-%m-%d')
    error_log.remove({'today': {'$lt': d_str}})
    req_log.remove({'today': {'$lt': d_str}})
    deviant_log.remove({'today': {'$lt': d_str}})


def send_jg_notification():
    """
    临时发送app 通知
    :return:
    """

    title = u'热量星球'
    content = u'【热量星球】每日邀请好友奖励上限升级到50人了，赶快邀请你的好友赚钱吧! 点击进入>>>'
    alert = {
        'title': title,
        'body': content
    }
    try:
        print jp_notification(alert, title, 'id', '')
    except:
        pass


def send_user_id_task():
    """
    发送用户信息队列
    :return:
    """
    user_cur = user.find({})
    for user_obj in user_cur:
        redis_code.lpush('user_id', str(user_obj.get('_id')))


def sync_leaderboard():
    """
    每日更新总的排行 榜数据
    :return:
    """
    while True:
        req_user_notice = redis_code.brpop('user_id', timeout=2)
        if not req_user_notice:
            break
        try:
            user_id = req_user_notice[1]
            print user_id
            user_obj = user.find_one({'_id': ObjectId(user_id)})

            # 计算邀请排行榜数据
            add_dict = {
                'user_id': user_id,
                'nickname': user_obj.get('nickname', ''),
                'phone': user_obj.get('phone', ''),
                'number_people_invited': 0,
                'number_people_invited2': 0,
                'status': user_obj.get('status', ''),
                'reg_time': user_obj.get('created_time')
            }
            number_people_invited = user.find({'invite_id': user_id}).count()
            if number_people_invited > 0:
                add_dict['number_people_invited'] = number_people_invited
                number_people_invited2 = user.find({'superior_invite_id': user_id}).count()
                add_dict['number_people_invited2'] = number_people_invited2
                invited_percentage = '%.2f' % (float(number_people_invited2) * 100 / float(number_people_invited)) + '%'
                add_dict['invited_percentage'] = invited_percentage
                Inviter_recursiver_obj = Inviter_recursiver()
                Inviter_recursiver_obj.calculate_inviter_recursiver(user_id)
                add_dict['total_invitation_num'] = Inviter_recursiver_obj.total
                leaderboard.update_one({'user_id': user_id}, {'$set': add_dict}, upsert=True)
            # 计算提现排行榜数据
            withdraw_total_dict = withdraw_record.aggregate([
                {
                    '$match': {'user_id': user_id, 'status': 1}
                },
                {
                    '$group': {'_id': '', 'withdraw_total': {'$sum': '$value'}}
                },
                {'$limit': 1}
            ])
            try:
                if isinstance(withdraw_total_dict, dict):

                    _withdraw_total_dict = withdraw_total_dict.get('result')[0]
                    withdraw_total = int(_withdraw_total_dict.get('withdraw_total'))
                else:
                    _withdraw_total_dict = withdraw_total_dict.next()
                    withdraw_total = int(_withdraw_total_dict.get('withdraw_total'))
            except:
                withdraw_total = 0

            if withdraw_total > 30:
                add_dict = {
                    'user_id': user_id,
                    'nickname': user_obj.get('nickname', ''),
                    'phone': user_obj.get('phone', ''),
                    'withdraw_value': float('%.2f' % (float(withdraw_total) / float(100))),
                    'status': user_obj.get('status', ''),
                    'balance': '%.2f' % (float(user_obj.get('balance', '')) / float(100)),
                    'reg_time': user_obj.get('created_time')
                }
                leaderboard_withdraw.update_one({'user_id': user_id}, {'$set': add_dict}, upsert=True)
        except Exception, e:
            print e


def send_user_notice_task():
    """
    发送有手机号的用户
    :return:
    """
    user_cur = user.find({'phone': {'$ne': ''}})
    for user_obj in user_cur:
        phone = user_obj.get('phone', '')
        if phone:
            redis_code.lpush('user_phone', phone)


def start_user_notice_task():
    """
    通过用户的活跃时间发送通知
    :return:
    """
    while True:
        req_user_notice = redis_code.brpop('user_phone', timeout=2)
        print req_user_notice
        if not req_user_notice:
            break
        phone = req_user_notice[1]
        user_obj = user.find_one({'phone': phone})

        user_id = str(user_obj.get('_id'))
        if user_offline_pullup.find_one({'user_id': user_id}):
            continue
        try:
            s_user_online_obj = s_user_online_t.find({'user_id': user_id}).sort([('today_str', -1)])[0]
            last_visit_time = s_user_online_obj.get('last_visit_time')
        except:
            last_visit_time = 0
        if last_visit_time > 0:
            if last_visit_time > (int(time.time()) - 60 * 60 * 24 * 3):
                continue
        if last_visit_time:
            offline_time = int(time.time()) - last_visit_time
            offline_day_num = int(offline_time / (60 * 60 * 24))
        else:
            offline_time = 60 * 60 * 24 * 30
            offline_day_num = 30
        print phone
        params_163 = '{"code":"https://dwz.cn/RuMxm0iM"}'
        response_json = send_sms_163(phone, params_163, '10910')
        if response_json.get('code') == 200:
            user_offline_pullup.insert_one({'user_id': user_id, 'offline_time': offline_time,
                                            'offline_day_num': offline_day_num})


def statistical_user_share(yesterday_str=timestamp_to_strftime((int(time.time()) - 24 * 60 * 60), format='%Y-%m-%d')):
    """
    统计用户各大占比数据
    :param yesterday_str:
    :return:
    """
    user_total_num = user.find().count()
    age_35 = user.find({'$and': [{'birth_year': {'$lte': '1984'}}, {'birth_year': {'$ne': ''}}]}).count()
    age_35_percentage = '%.2f' % (float(age_35) * 100 / float(user_total_num)) + '%'

    age_25_35 = user.find({'birth_year': {'$gt': '1984', '$lte': '1994'}}).count()
    age_25_35_percentage = '%.2f' % (float(age_25_35) * 100 / float(user_total_num)) + '%'
    age_18_25 = user.find({'birth_year': {'$gt': '1994', '$lte': '2001'}}).count()
    age_18_25_percentage = '%.2f' % (float(age_18_25) * 100 / float(user_total_num)) + '%'
    age_18 = user.find({'birth_year': {'$gt': '2001'}}).count()
    age_18_percentage = '%.2f' % (float(age_18) * 100 / float(user_total_num)) + '%'
    age_unknown = user.find({'birth_year': ''}).count()
    age_unknown_percentage = '%.2f' % (float(age_unknown) * 100 / float(user_total_num)) + '%'
    sex_male = user.find({'sex': 1}).count()
    sex_male_percentage = '%.2f' % (float(sex_male) / float(user_total_num)) + '%'
    sex_female = user.find({'sex': 2}).count()
    sex_female_percentage = '%.2f' % (float(sex_female) * 100 / float(user_total_num)) + '%'
    sex_unknown = user.find({'sex': 0}).count()
    sex_unknown_percentage = '%.2f' % (float(sex_unknown) * 100 / float(user_total_num)) + '%'

    sys_ios = user.find({'mp_system_type': 'ios'}).count()
    sys_ios_percentage = '%.2f' % (float(sys_ios) * 100 / float(user_total_num)) + '%'
    sys_android = user.find({'mp_system_type': 'android'}).count()
    sys_android_percentage = '%.2f' % (float(sys_android) * 100 / float(user_total_num)) + '%'

    balance_50 = user.find({'balance': {'$gte': 5000}}).count()
    balance_50_percentage = '%.2f' % (float(balance_50) * 100 / float(user_total_num)) + '%'
    user_balance_dict = user.aggregate([
        {
            '$match': {'balance': {'$gte': 5000}}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_50_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_50_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_50_total = 0
    balance_50_total = '%.2f' % (float(balance_50_total) / float(100))
    balance_40_50 = user.find({'$and': [{'balance': {'$lt': 5000}}, {'balance': {'$gte': 4000}}]}).count()
    balance_40_50_percentage = '%.2f' % (float(balance_40_50) * 100 / float(user_total_num)) + '%'
    user_balance_dict = user.aggregate([
        {
            '$match': {'$and': [{'balance': {'$lt': 5000}}, {'balance': {'$gte': 4000}}]}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_40_50_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_40_50_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_40_50_total = 0
    balance_40_50_total = '%.2f' % (float(balance_40_50_total) / float(100))
    balance_30_40 = user.find({'$and': [{'balance': {'$lt': 4000}}, {'balance': {'$gte': 3000}}]}).count()
    balance_30_40_percentage = '%.2f' % (float(balance_30_40) * 100 / float(user_total_num)) + '%'
    user_balance_dict = user.aggregate([
        {
            '$match': {'$and': [{'balance': {'$lt': 4000}}, {'balance': {'$gte': 3000}}]}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_30_40_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_30_40_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_30_40_total = 0
    balance_30_40_total = '%.2f' % (float(balance_30_40_total) / float(100))
    balance_20_30 = user.find({'$and': [{'balance': {'$lt': 3000}}, {'balance': {'$gte': 2000}}]}).count()
    balance_20_30_percentage = '%.2f' % (float(balance_20_30) * 100 / float(user_total_num)) + '%'
    user_balance_dict = user.aggregate([
        {
            '$match': {'$and': [{'balance': {'$lt': 3000}}, {'balance': {'$gte': 2000}}]}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_20_30_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_20_30_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_20_30_total = 0
    balance_20_30_total = '%.2f' % (float(balance_20_30_total) / float(100))
    balance_10_20 = user.find({'$and': [{'balance': {'$lt': 2000}}, {'balance': {'$gte': 1000}}]}).count()
    balance_10_20_percentage = '%.2f' % (float(balance_10_20) * 100 / float(user_total_num)) + '%'
    user_balance_dict = user.aggregate([
        {
            '$match': {'$and': [{'balance': {'$lt': 2000}}, {'balance': {'$gte': 1000}}]}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_10_20_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_10_20_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_10_20_total = 0
    balance_10_20_total = '%.2f' % (float(balance_10_20_total) / float(100))
    balance_5_10 = user.find({'$and': [{'balance': {'$lt': 1000}}, {'balance': {'$gte': 500}}]}).count()
    balance_5_10_percentage = '%.2f' % (float(balance_5_10) * 100 / float(user_total_num)) + '%'
    user_balance_dict = user.aggregate([
        {
            '$match': {'$and': [{'balance': {'$lt': 1000}}, {'balance': {'$gte': 500}}]}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_5_10_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_5_10_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_5_10_total = 0
    balance_5_10_total = '%.2f' % (float(balance_5_10_total) / float(100))
    balance_5 = user.find({'balance': {'$lt': 500}}).count()
    balance_5_percentage = '%.2f' % (float(balance_5) * 100 / float(user_total_num)) + '%'
    user_balance_dict = user.aggregate([
        {
            '$match': {'balance': {'$lt': 500}}
        },
        {
            '$group': {'_id': '', 'balance_total': {'$sum': '$balance'}}
        },
        {'$limit': 1}
    ])
    try:
        if isinstance(user_balance_dict, dict):

            _user_balance_dict = user_balance_dict.get('result')[0]
            balance_5_total = int(_user_balance_dict.get('balance_total'))
        else:
            _user_balance_dict = user_balance_dict.next()
            balance_5_total = int(_user_balance_dict.get('balance_total'))
    except:
        balance_5_total = 0
    balance_5_total = '%.2f' % (float(balance_5_total) / float(100))
    statistical_day.update_one({'today_str': yesterday_str},
                               {'$set': {'age_35': age_35, 'age_35_percentage': age_35_percentage,
                                         'age_25_35': age_25_35, 'age_25_35_percentage': age_25_35_percentage,
                                         'age_18_25': age_18_25, 'age_18_25_percentage': age_18_25_percentage,
                                         'age_18': age_18, 'age_18_percentage': age_18_percentage,
                                         'age_unknown': age_unknown, 'age_unknown_percentage': age_unknown_percentage,
                                         'sex_male': sex_male, 'sex_male_percentage': sex_male_percentage,
                                         'sex_female': sex_female, 'sex_female_percentage': sex_female_percentage,
                                         'sex_unknown': sex_unknown, 'sex_unknown_percentage': sex_unknown_percentage,
                                         'sys_ios': sys_ios, 'sys_ios_percentage': sys_ios_percentage,
                                         'sys_android': sys_android, 'sys_android_percentage': sys_android_percentage,
                                         'balance_50': balance_50, 'balance_50_percentage': balance_50_percentage,
                                         'balance_50_total': balance_50_total, 'balance_40_50': balance_40_50,
                                         'balance_40_50_percentage': balance_40_50_percentage,
                                         'balance_40_50_total': balance_40_50_total, 'balance_30_40': balance_30_40,
                                         'balance_30_40_percentage': balance_30_40_percentage,
                                         'balance_30_40_total': balance_30_40_total, 'balance_20_30': balance_20_30,
                                         'balance_20_30_percentage': balance_20_30_percentage,
                                         'balance_20_30_total': balance_20_30_total, 'balance_10_20': balance_10_20,
                                         'balance_10_20_percentage': balance_10_20_percentage,
                                         'balance_10_20_total': balance_10_20_total, 'balance_5_10': balance_5_10,
                                         'balance_5_10_percentage': balance_5_10_percentage,
                                         'balance_5_10_total': balance_5_10_total, 'balance_5': balance_5,
                                         'balance_5_percentage': balance_5_percentage,
                                         'balance_5_total': balance_5_total}}, upsert=True)


def check_planet_commission():
    """
    检查星球的分润是否解冻
    :return:
    """
    user_cur = user.find({'grade': 1})
    for user_obj in user_cur:
        planet_id = user_obj.get('planet_id', '')
        if planet_id:
            if commission_record.find({'planet_id': planet_id, 'is_arrival': 0}).count() > 0:
                planet_commission_dict = commission_record.aggregate([
                    {
                        '$match': {'planet_id': planet_id, 'is_arrival': 0}
                    },
                    {
                        '$group': {'_id': '', 'planet_commission': {'$sum': '$value'}}
                    },
                    {'$limit': 1}
                ])
                try:
                    if isinstance(planet_commission_dict, dict):

                        _planet_commission_dict = planet_commission_dict.get('result')[0]
                        planet_commission = int(_planet_commission_dict.get('planet_commission'))
                    else:
                        _planet_commission_dict = planet_commission_dict.next()
                        planet_commission = int(_planet_commission_dict.get('planet_commission'))
                except:
                    planet_commission = 0
                if planet_commission:
                    user.update_one({'_id': ObjectId(planet_id)},
                                    {'$inc': {'planet_commission_total': planet_commission,
                                              'balance': planet_commission}})
                    commission_record.update_many({'planet_id': planet_id, 'is_arrival': 0},
                                                  {'$set': {'is_arrival': 1}})

                user.update_many({'invite_id': planet_id}, {'$set': {'superior_planet_id': planet_id}})
                user.update_many({'superior_invite_id': planet_id},
                                 {'$set': {'upperlevel_planet_id': planet_id}})


def generate_statistical_official():
    """
    官方推广访问统计
    :return:
    """

    earth_code_list = earth_code.find({})
    for earth_code_obj in earth_code_list:
        access_today = earth_code_obj.get('access_today')
        invite_code = earth_code_obj.get('invite_code')

        today_str = timestamp_to_strftime((int(time.time()) - 24 * 60 * 60), format='%Y-%m-%d')
        first_level_invitation_num = user.find({'invite_id': invite_code,
                                                'created_time': {'$regex': today_str}}).count()
        sencond_level_invitation_num = user.find({'superior_invite_id': invite_code,
                                                  'created_time': {'$regex': today_str}}).count()
        Inviter_recursiver_obj = Inviter_recursiver()
        Inviter_recursiver_obj.calculate_inviter_recursiver(invite_code, today_str)
        total_invitation_num = Inviter_recursiver_obj.total

        statistical_day_official.update_one({'today_str': today_str, 'invite_code': invite_code},
                                            {'$set': {'first_level_invitation_num': first_level_invitation_num,
                                                      'sencond_level_invitation_num': sencond_level_invitation_num,
                                                      'total_invitation_num': total_invitation_num,
                                                      'access_today': access_today,
                                                      'invite_name': earth_code_obj.get('remark')}}, upsert=True)

        first_level_invitation_num = user.find({'invite_id': invite_code}).count()
        sencond_level_invitation_num = user.find({'superior_invite_id': invite_code}).count()
        Inviter_recursiver_obj = Inviter_recursiver()
        Inviter_recursiver_obj.calculate_inviter_recursiver(invite_code)
        total_invitation_num = Inviter_recursiver_obj.total
        earth_code.update_one({'invite_code': invite_code},
                              {'$set': {'first_level_invitation_num': first_level_invitation_num,
                                        'sencond_level_invitation_num': sencond_level_invitation_num,
                                        'total_invitation_num': total_invitation_num, 'access_today': 0,
                                        'access_yestoday': access_today}})


def calculate_planet(operation_obj, user_obj, real_value, is_commission=True):
    planet_id = user_obj.get('planet_id', '')
    superior_planet_id = user_obj.get('superior_planet_id', '')
    upperlevel_planet_id = user_obj.get('upperlevel_planet_id', '')
    invite_id = user_obj.get('invite_id', '')
    superior_invite_id = user_obj.get('superior_invite_id', '')

    if is_commission:
        commission_percent_1 = operation_obj.get('commission_percent_1', 10)
        commission_percent_2 = operation_obj.get('commission_percent_2', 5)
        commission_1 = int(real_value * commission_percent_1 / 100)
        commission_2 = int(real_value * commission_percent_2 / 100)
        # 有邀请人一级分润
        if invite_id:
            # 有上级分润 且上级是真实用户邀请
            if commission_1 and ObjectId.is_valid(invite_id):
                planet_obj = user.find_one({'_id': ObjectId(invite_id)})
                if planet_obj:
                    planet_balance = planet_obj.get('balance', '')
                    user.update_one({'_id': planet_obj.get('_id')},
                                    {'$inc': {'planet_commission_total': commission_1, 'balance': commission_1}})
                    serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'),
                                                                   get_chars2(0, 1),
                                                                   datetime.now().strftime(format='%m'),
                                                                   get_chars2(0, 1),
                                                                   datetime.now().strftime(format='%d'),
                                                                   get_chars2(0, 1),
                                                                   datetime.now().strftime(format='%H%M%S'))
                    commission_record.insert_one({'serial_number': serial_number, 'planet_id': invite_id,
                                                  'origin': u'转发文章获得{0}元'.format(
                                                      '%.2f' % (float(real_value) / float(100))),
                                                  'value': int(commission_1),
                                                  'balance': int(commission_1 + planet_balance),
                                                  'user_id': invite_id, 'user_name': user_obj.get('nickname'),
                                                  'contributor_id': str(user_obj.get('_id')), 'is_arrival': 1,
                                                  'user_img': user_obj.get('headimgurl'), 'grade': 2, 'type_num': 0,
                                                  'today': datetime.now().strftime(format='%Y-%m-%d'),
                                                  'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
                    if commission_record.find({'planet_id': invite_id, 'type_num': 0, 'grade': 2}).count() == 1:
                        redis_invite_code.lpush('invite_json',
                                                json.dumps({'is_bind': 10, 'invite_id': invite_id, 'grade': 2,
                                                            'value': '%.2f' % (float(commission_1) / float(100)) + u'元',
                                                            'nickname': u'原住居民' + user_obj.get('nickname')}))
        # 有上级邀请人二级分润
        if superior_invite_id:

            if commission_2 and ObjectId.is_valid(superior_invite_id):
                # 有上上级分润
                serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%m'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%d'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%H%M%S'))

                planet_obj = user.find_one({'_id': ObjectId(superior_invite_id)})
                if planet_obj:
                    planet_balance = planet_obj.get('balance', '')
                    user.update_one({'_id': planet_obj.get('_id')},
                                    {'$inc': {'planet_commission_total': commission_2, 'balance': commission_2}})

                    commission_record.insert_one({'serial_number': serial_number, 'planet_id': superior_invite_id,
                                                  'origin': u'转发文章获得{0}元'.format(
                                                      '%.2f' % (float(real_value) / float(100))),
                                                  'value': int(commission_2),
                                                  'balance': int(commission_2 + planet_balance),
                                                  'user_id': superior_invite_id, 'user_name': user_obj.get('nickname'),
                                                  'contributor_id': str(user_obj.get('_id')), 'is_arrival': 1,
                                                  'user_img': user_obj.get('headimgurl'), 'grade': 3, 'type_num': 0,
                                                  'today': datetime.now().strftime(format='%Y-%m-%d'),
                                                  'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
                    if commission_record.find(
                            {'planet_id': superior_invite_id, 'type_num': 0, 'grade': 3}).count() == 1:
                        redis_invite_code.lpush('invite_json',
                                                json.dumps({'is_bind': 10, 'invite_id': superior_invite_id, 'grade': 3,
                                                            'value': '%.2f' % (float(commission_2) / float(100)) + u'元',
                                                            'nickname': u'附属居民' + user_obj.get('nickname')}))

    # 为所有所属星球增加总红包金额
    if planet_id:
        if planet_id == '88888888':
            system.update_one({}, {'$inc': {'planet_red_total': real_value}})
        else:
            planet_obj = user.find_one({'_id': ObjectId(planet_id)})
            user.update_one({'_id': planet_obj.get('_id')}, {'$inc': {'planet_red_total': real_value}})
    if superior_planet_id:
        if superior_planet_id == '88888888':
            system.update_one({}, {'$inc': {'planet_red_total': real_value}})
        else:
            planet_obj = user.find_one({'_id': ObjectId(superior_planet_id)})
            user.update_one({'_id': planet_obj.get('_id')}, {'$inc': {'planet_red_total': real_value}})
    if upperlevel_planet_id:
        if upperlevel_planet_id == '88888888':
            system.update_one({}, {'$inc': {'planet_red_total': real_value}})
        else:
            planet_obj = user.find_one({'_id': ObjectId(upperlevel_planet_id)})
            user.update_one({'_id': planet_obj.get('_id')}, {'$inc': {'planet_red_total': real_value}})
    return real_value


def third_transfer_profit():
    """
    :param os: 1为安卓，2为ios
    :param uid: 用户唯 一id
    :return:
    """
    yesterday_str = timestamp_to_strftime((int(time.time()) - 24 * 60 * 60), format='%Y-%m-%d')
    operation_obj = operation.find_one()
    wechat_transfer_cash = int(operation_obj.get('wechat_transfer_cash', 10))
    wechat_transfer_calorific = int(operation_obj.get('wechat_transfer_calorific', 5))
    wechat_transfer_per_deduction = int(operation_obj.get('wechat_transfer_per_deduction', 10))
    user_cur = user.find({'status': 0})
    for user_obj in user_cur:
        user_id = str(user_obj.get('_id'))
        third_transfer_art_token = user_obj.get('third_transfer_art_token')
        if third_transfer_art_token:
            redis_admin.lpush('third_transfer_profit',
                              json.dumps({'third_transfer_art_token': third_transfer_art_token, 'user_id': user_id}))
    while True:
        try:
            third_transfer_profit_req = redis_admin.brpop('third_transfer_profit', timeout=2)
            if not third_transfer_profit_req:
                break
            third_transfer_profit_dict = json.loads(third_transfer_profit_req[1])
            user_id = third_transfer_profit_dict.get('user_id')
            user_obj = user.find_one({'_id': ObjectId(user_id)})
            planet_id = user_obj.get('planet_id', '')
            superior_planet_id = user_obj.get('superior_planet_id', '')
            upperlevel_planet_id = user_obj.get('upperlevel_planet_id', '')
            if planet_id:
                current_planet_id = planet_id
            elif superior_planet_id:
                current_planet_id = superior_planet_id
            else:
                current_planet_id = upperlevel_planet_id
            third_transfer_art_token = third_transfer_profit_dict.get('third_transfer_art_token')
            json_data = {}
            for i in range(3):
                try:
                    ts = int(time.time() * 1000)
                    uuid_m = hashlib.md5(str(uuid.uuid4()).replace('-', ''))
                    opt = {'day': yesterday_str, 'token': third_transfer_art_token, 'uuid': uuid_m.hexdigest(),
                           'ts': ts}
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
                                         headers={'sign': md5_text, 'Content-Type': 'multipart/form-data'}, params=opt)
                    req_json = resp.json()
                    if req_json.get('code') == 0 and req_json.get('data', {}):
                        json_data = req_json.get('data', {})
                        break
                except Exception, e:
                    continue
            if json_data:
                ips = json_data.get('ips', 0)
                if ips:
                    real_ips = ips - int(wechat_transfer_per_deduction * ips / 100)
                    real_value = wechat_transfer_cash * real_ips
                    s_user_online_t.update_one({'today_str': yesterday_str, 'user_id': user_id},
                                               {'$set': {'show_wechat_transfer_ips': real_ips,
                                                         'show_cash': real_value, 'wechat_transfer_ips': ips}})
                    real_calorific = wechat_transfer_calorific * real_ips
                    # 收益 记录
                    if not red_record.find_one({'origin': u'转发文章有效阅读收益', 'user_id': user_id,
                                                'today': datetime.now().strftime(format='%Y-%m-%d')}):
                        serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%m'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%d'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%H%M%S'))
                        red_record_dict = {'serial_number': serial_number, 'origin': u'转发文章有效阅读收益',
                                           'value': int(real_value),
                                           'balance': int(real_value + user_obj.get('balance')),
                                           'user_id': user_id, 'user_name': user_obj.get('nickname'),
                                           'user_img': user_obj.get('headimgurl'), 'type_num': 3, 'hour_int': 0,
                                           'today': datetime.now().strftime(format='%Y-%m-%d'),
                                           'planet_id': planet_id, 'superior_planet_id': superior_planet_id,
                                           'is_double': 1,
                                           'current_planet_id': current_planet_id,
                                           'upperlevel_planet_id': upperlevel_planet_id, 'red_returnp_calorific': 0,
                                           'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}
                        red_record.insert_one(red_record_dict)
                        calculate_planet(operation_obj, user_obj, real_value)
                        user.update_one({'_id': ObjectId(user_obj.get('_id'))},
                                        {'$inc': {'balance': int(real_value), 'red_total': int(real_value)}})
                    if not calorific_record.find_one({'user_id': user_id,
                                                      'today': datetime.now().strftime(format='%Y-%m-%d'),
                                                      'des': u'转发文章有效阅读奖热量'}):
                        calorific_record.insert_one(
                            {'user_id': user_id, 'today': datetime.now().strftime(format='%Y-%m-%d'), 'symbol': 1,
                             'type_num': 12, 'value': real_calorific, 'des': u'转发文章有效阅读奖热量', 'red_id': '',
                             'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
                        user.update_one({'_id': ObjectId(user_id)},
                                        {'$inc': {'available_calorific': real_calorific,
                                                  'calorific_total': real_calorific}})
        except:
            pass


def transfer_activity_reward():
    """
    转发活动奖励
    :return:
    """
    yesterday_str = timestamp_to_strftime((int(time.time()) - 24 * 60 * 60), format='%Y-%m-%d')
    if '2019-11-10' < yesterday_str < '2019-11-18':
        operation_obj = operation.find_one()
        reward_vluae_cashe_total = 100000
        reward_vluae_cashe = 100
        wechat_transfer_cash = operation_obj.get('wechat_transfer_cash', 20)
        reward_transfer_ips = int(reward_vluae_cashe / wechat_transfer_cash)
        reward_user_number = s_user_online_t.find({'today_str': yesterday_str,
                                                   'show_wechat_transfer_ips': {'$gte': reward_transfer_ips}}).count()

        reward_vluae_cashe_avg = int(reward_vluae_cashe_total / (reward_user_number * 7))

        s_user_online_t_cur = s_user_online_t.find({'today_str': yesterday_str,
                                                    'show_wechat_transfer_ips': {'$gte': reward_transfer_ips}})

        for s_user_online_t_obj in s_user_online_t_cur:
            user_id = s_user_online_t_obj.get('user_id')
            user_obj = user.find_one({'_id': ObjectId(user_id)})
            planet_id = user_obj.get('planet_id', '')
            superior_planet_id = user_obj.get('superior_planet_id', '')
            upperlevel_planet_id = user_obj.get('upperlevel_planet_id', '')
            if planet_id:
                current_planet_id = planet_id
            elif superior_planet_id:
                current_planet_id = superior_planet_id
            else:
                current_planet_id = upperlevel_planet_id
            serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'),
                                                           get_chars2(0, 1),
                                                           datetime.now().strftime(format='%m'),
                                                           get_chars2(0, 1),
                                                           datetime.now().strftime(format='%d'),
                                                           get_chars2(0, 1),
                                                           datetime.now().strftime(format='%H%M%S'))
            red_record_dict = {'serial_number': serial_number, 'origin': u'转发文章活动奖励',
                               'value': reward_vluae_cashe_avg,
                               'balance': int(reward_vluae_cashe_avg + user_obj.get('balance')),
                               'user_id': user_id, 'user_name': user_obj.get('nickname'),
                               'user_img': user_obj.get('headimgurl'), 'type_num': 3, 'hour_int': 0,
                               'today': datetime.now().strftime(format='%Y-%m-%d'),
                               'planet_id': planet_id, 'superior_planet_id': superior_planet_id,
                               'is_double': 1,
                               'current_planet_id': current_planet_id,
                               'upperlevel_planet_id': upperlevel_planet_id, 'red_returnp_calorific': 0,
                               'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}
            red_record.insert_one(red_record_dict)
            user.update_one({'_id': ObjectId(user_id)}, {'$inc': {'balance': int(reward_vluae_cashe_avg),
                                                                  'red_total': int(reward_vluae_cashe_avg)}})


if __name__ == '__main__':
    try:
        # 统计转发文章收益
        third_transfer_profit()
    except:
        pass
    try:
        # 官方推广访问统计
        generate_statistical_official()
    except Exception, e:
        print e
    try:
        # 生成昨天 报表数据
        generate_statistical_day()
    except:
        pass
    try:
        # 更新留存率
        generate_statistical_retain()
    except:
        pass
    try:
        # 删除 用户在线时长统计表一个月前的数据
        delete_user_online_data()
    except:
        pass
    try:
        # 生成广告统计表
        generate_ad_statistical_day()
    except:
        pass
    try:
        # 统计用户各大占比数据
        statistical_user_share()
    except:
        pass
    try:
        # 发送用户任务
        send_user_id_task()
    except:
        pass
    try:
        # 统计排行榜
        sync_leaderboard()
    except:
        pass
    try:
        transfer_activity_reward()
    except:
        pass
