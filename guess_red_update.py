# -*- coding: utf-8 -*-

import json
import sys
import time
from datetime import datetime

from bson import ObjectId

from libs.db import (operation, redis_admin, error_log, guess_red_detail, guess_red, user, red_record,
                     calorific_record, commission_record, redis_invite_code, system)
from libs.utils import get_chars2

reload(sys)
sys.setdefaultencoding('utf-8')


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
                planet_balance = planet_obj.get('balance', '')
                user.update_one({'_id': planet_obj.get('_id')},
                                {'$inc': {'planet_commission_total': commission_1, 'balance': commission_1}})
                serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%m'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%d'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%H%M%S'))
                commission_record.insert_one({'serial_number': serial_number, 'planet_id': invite_id,
                                              'origin': u'猜红包获得{0}元'.format('%.2f' % (float(real_value) / float(100))),
                                              'value': int(commission_1), 'balance': int(commission_1 + planet_balance),
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
                planet_balance = planet_obj.get('balance', '')
                user.update_one({'_id': planet_obj.get('_id')},
                                {'$inc': {'planet_commission_total': commission_2, 'balance': commission_2}})

                commission_record.insert_one({'serial_number': serial_number, 'planet_id': superior_invite_id,
                                              'origin': u'猜红包获得{0}元'.format('%.2f' % (float(real_value) / float(100))),
                                              'value': int(commission_2), 'balance': int(commission_2 + planet_balance),
                                              'user_id': superior_invite_id, 'user_name': user_obj.get('nickname'),
                                              'contributor_id': str(user_obj.get('_id')), 'is_arrival': 1,
                                              'user_img': user_obj.get('headimgurl'), 'grade': 3, 'type_num': 0,
                                              'today': datetime.now().strftime(format='%Y-%m-%d'),
                                              'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
                if commission_record.find({'planet_id': superior_invite_id, 'type_num': 0, 'grade': 3}).count() == 1:
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


def update_guess_red_detail():
    """
    排队处理猜中红包的用户
    :return:
    """
    hour_str = datetime.now().strftime(format='%H')
    operation_obj = operation.find_one()
    while True:
        guess_red_task = redis_admin.brpop('guess_red_id_list', timeout=1)
        if not guess_red_task:
            new_hour_str = datetime.now().strftime(format='%H')
            if new_hour_str != hour_str:
                break
            continue
        try:
            guess_red_id = guess_red_task[1]
            guess_red_detail_obj = guess_red_detail.find_one({'_id': ObjectId(guess_red_id)})
            if not guess_red_detail_obj:
                continue
            number_of_periods = guess_red_detail_obj.get('number_of_periods')
            guess_red_obj = guess_red.find_one({'number_of_periods': number_of_periods})
            if not guess_red_obj:
                continue
            user_id = guess_red_obj.get('user_id', '')
            # 第一个猜中 领取红包
            if not user_id:
                user_id = guess_red_detail_obj.get('user_id')
                user_obj = user.find_one({'_id': ObjectId(user_id)})
                planet_id = user_obj.get('planet_id', '')
                superior_planet_id = user_obj.get('superior_planet_id', '')
                upperlevel_planet_id = user_obj.get('upperlevel_planet_id', '')

                guess_red_detail.update_one({'_id': guess_red_detail_obj.get('_id')}, {'$set': {'status': 1}})
                real_value = guess_red_obj.get('value')
                hour_int = guess_red_obj.get('hour_int')
                # 计算星球分润与星球总红包
                try:
                    calculate_planet(operation_obj, user_obj, real_value)
                except:
                    pass
                # 红包记录
                serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%m'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%d'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%H%M%S'))
                if planet_id:
                    current_planet_id = planet_id
                elif superior_planet_id:
                    current_planet_id = superior_planet_id
                else:
                    current_planet_id = upperlevel_planet_id
                red_record_dict = {'serial_number': serial_number, 'origin': u'猜中红包', 'value': int(real_value),
                                   'balance': int(real_value + user_obj.get('balance')), 'user_id': user_id,
                                   'user_name': user_obj.get('nickname'), 'user_img': user_obj.get('headimgurl'),
                                   'today': guess_red_obj.get('today_str'), 'type_num': 2, 'hour_int': hour_int,
                                   'planet_id': planet_id, 'superior_planet_id': superior_planet_id, 'is_double': 0,
                                   'current_planet_id': current_planet_id, 'upperlevel_planet_id': upperlevel_planet_id,
                                   'red_returnp_calorific': 0,
                                   'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}
                red_record.insert_one(red_record_dict)
                user.update_one({'_id': ObjectId(user_id)},
                                {'$inc': {'balance': int(real_value), 'red_total': int(real_value)}})
                guess_red.update_one({'number_of_periods': number_of_periods},
                                     {'$set': {'nickname': user_obj.get('nickname'), 'user_id': user_id,
                                               'headimgurl': user_obj.get('headimgurl', ''),
                                               'guess_time': guess_red_detail_obj.get('guess_time', ''),
                                               'millisecond': guess_red_detail_obj.get('millisecond', ''),
                                               'status': 1}})
            else:
                # 不是第一个猜中 返热量
                user_id = guess_red_detail_obj.get('user_id')
                consume_calorific = guess_red_detail_obj.get('consume_calorific')
                calorific_record.insert_one({'user_id': user_id, 'today': guess_red_obj.get('today_str'), 'symbol': 1,
                                             'type_num': 3, 'value': consume_calorific * 2,
                                             'des': u'猜中红包但晚了一步奖热量', 'red_id': number_of_periods,
                                             'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
                user.update_one({'_id': ObjectId(user_id)},
                                {'$inc': {'available_calorific': consume_calorific * 2,
                                          'calorific_total': consume_calorific * 2}})
                guess_red_detail.update_one({'_id': guess_red_detail_obj.get('_id')}, {'$set': {'status': 2}})
        except Exception, e:
            error_log.insert_one({'req_url': '', 'req_data': '', 'req_method': 'update_guess_red_detail',
                                  'error_str': str(e), 'today': datetime.now().strftime(format='%Y-%m-%d'),
                                  'time_stamp': int(time.time()),
                                  'req_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})

        new_hour_str = datetime.now().strftime(format='%H')
        if new_hour_str != hour_str:
            break


# 每小时执行一次的脚本
if __name__ == '__main__':
    try:
        # 排队处理猜中红包的用户
        update_guess_red_detail()
    except:
        pass
