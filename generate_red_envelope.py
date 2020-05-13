# -*- coding: utf8 -*-
import json
import random
import sys
import time
from datetime import datetime

from bson import ObjectId

from libs.db import (operation, dividend_config, integer_red, integer_red_detail, redis_admin, guess_red, user,
                     commission_record, redis_invite_code, calorific_record)
from libs.utils import timestamp_to_strftime, get_chars2

reload(sys)
sys.setdefaultencoding('utf-8')


def reservation_hongbao(money, envelope_num, lowest_value, multiple):
    """
    通过预算红包金额、红包个数 生成随机红包
    :param money:  红包金额大小（单位）
    :param envelope_num:大概生成的红包个数
    :param lowest_value:红包区间最小的红包值
    :param multiple: 红包区间最大的红包值为平均值 的多少倍
    :return:
    """
    # 当前剩余的钱，初始值为money
    red_dict = {'total_value': 0, 'red_list': []}
    total_value = 0
    current_money = money
    red_list = []
    lave_num = envelope_num
    if envelope_num == 1:
        return [money]
    for i in range(1, envelope_num + 1):
        get_money = random.randint(lowest_value, int(multiple * current_money / lave_num))
        current_money -= get_money
        red_list.append(get_money)
        total_value += get_money
        if current_money <= 0:
            break
        if current_money <= lowest_value:
            if current_money != 0:
                red_list.append(lowest_value)
                total_value += lowest_value
            break
        lave_num -= 1
        if lave_num == 1 and current_money > 0:
            red_list.append(current_money)
            total_value += current_money
            break
        if int(multiple * current_money / lave_num) < lowest_value:
            red_list.append(lowest_value)
            total_value += lowest_value
            break
    red_dict['red_list'] = red_list
    red_dict['total_value'] = total_value
    return red_dict


def interval_red_envelope(envelope_num, lowest_value, maximum_value):
    """
    通过红包区间与红包个数 生成红包
    :param envelope_num: 红包个数
    :param lowest_value: 红包的最小金额
    :param maximum_value: 红包的最大金额
    :return:
    """
    red_dict = {'total_value': 0, 'red_list': []}
    total_value = 0
    red_list = []
    if envelope_num > 0:
        for i in range(1, envelope_num + 1):
            get_money = random.randint(lowest_value, maximum_value)
            total_value += get_money
            red_list.append(get_money)
        red_dict.update({'total_value': total_value, 'red_list': red_list})
    return red_dict


def generate_integer_red():
    """
    生成整点红包
    :return:
    """

    operation_obj = operation.find_one()
    integer_red_number = int(operation_obj.get('integer_red_number', 100))
    red_hour_per_json = json.loads(operation_obj.get('red_hour_per_json'))

    dividend_config_obj = dividend_config.find({}).sort([('today_str', -1)])[0]
    integer_red_value = dividend_config_obj.get('integer_red_value', 0) * 100 / 115

    if integer_red_value:
        for hour_int in range(24):
            hour_dict = red_hour_per_json.get(str(hour_int))
            # 红包所占资金比例
            per = hour_dict.get('per')
            # 此红包的总金额
            value = per * integer_red_value
            # 红包大概个数
            envelope_num = integer_red_number * per
            # 5到10块红包占比百分之二 所发红包数量为
            envelope_5_10_num = int(2 * envelope_num / 100)
            red_envelope_5_10_dict = interval_red_envelope(envelope_5_10_num, 500, 1100)
            # 5到10块红包所发红包金额为:
            total_5_10_value = red_envelope_5_10_dict.get('total_value')
            # 5到10块红包所发红包列表为
            red_5_10_list = red_envelope_5_10_dict.get('red_list')

            # 1到5块红包占比百分之三 所发红包数量为
            envelope_1_5_num = int(3 * envelope_num / 100)
            red_envelope_1_5_dict = interval_red_envelope(envelope_1_5_num, 100, 500)
            # 1到5块红包所发红包金额为:
            total_1_5_value = red_envelope_1_5_dict.get('total_value')
            # 5到10块红包所发红包列表为
            red_1_5_list = red_envelope_1_5_dict.get('red_list')

            # 其它金额的红包列表
            red_dict = reservation_hongbao(value - total_5_10_value - total_1_5_value, envelope_num, 10, 5)
            red_list = red_dict.get('red_list')
            total_value = red_dict.get('total_value')
            today_str = timestamp_to_strftime(time.time() + 24 * 60 * 60, format='%Y-%m-%d')
            timeArray = time.strptime('{0} {1}:00:00'.format(today_str, hour_int), "%Y-%m-%d %H:%M:%S")
            start_time = int(time.mktime(timeArray))
            integer_red_dict = {'today_str': today_str, 'hour_int': hour_int,
                                'value': total_value + total_5_10_value + total_1_5_value,
                                'number': len(red_list) + len(red_5_10_list) + len(red_1_5_list),
                                'status': 0, 'start_time': start_time}
            integer_red.insert_one(integer_red_dict)
            integer_red_id = str(integer_red_dict.get('_id'))

            for i in range(len(red_list)):
                # 随机插入一个五到十块的红包
                if random.randint(0, 25) == 10:
                    if red_5_10_list:
                        integer_red_detail.insert_one(
                            {'integer_red_id': integer_red_id, 'value': red_5_10_list.pop(), 'user_id': '',
                             'optimum': 0})
                else:
                    # 随机插入一个1到5块的红包
                    if random.randint(0, 17) == 10:
                        if red_1_5_list:
                            integer_red_detail.insert_one(
                                {'integer_red_id': integer_red_id, 'value': red_1_5_list.pop(), 'user_id': '',
                                 'optimum': 0})
                if random.randint(0, 1):
                    red_value = red_list.pop(0)
                else:
                    red_value = red_list.pop(-1)

                integer_red_detail.insert_one({'integer_red_id': integer_red_id, 'value': red_value, 'user_id': '',
                                               'optimum': 0})

            for red_value in red_5_10_list:
                integer_red_detail.insert_one({'integer_red_id': integer_red_id, 'value': red_value, 'user_id': '',
                                               'optimum': 0})
            for red_value in red_1_5_list:
                integer_red_detail.insert_one({'integer_red_id': integer_red_id, 'value': red_value, 'user_id': '',
                                               'optimum': 0})
            max_red_value = 0
            max_integer_red_id = ''
            integer_red_detail_cur = integer_red_detail.find({'integer_red_id': integer_red_id})
            for integer_red_detail_obj in integer_red_detail_cur:
                if integer_red_detail_obj.get('value') > max_red_value:
                    max_red_value = integer_red_detail_obj.get('value')
                    max_integer_red_id = integer_red_detail_obj.get('_id')
                redis_admin.lpush('integer_red_id_' + integer_red_id, str(integer_red_detail_obj.get('_id')))
            integer_red_detail.update_one({'_id': max_integer_red_id}, {'$set': {'optimum': 1}})


def generate_guess_red():
    """
    生成猜红包数据
    :return:
    """
    operation_obj = operation.find_one()
    today_str = timestamp_to_strftime(time.time() + 24 * 60 * 60, format='%Y-%m-%d')
    guess_red_invalid_time = int(operation_obj.get('guess_red_invalid_time', 5))
    red_hour_per_json = json.loads(operation_obj.get('red_hour_per_json'))
    dividend_config_obj = dividend_config.find({}).sort([('today_str', -1)])[0]
    guess_red_value = dividend_config_obj.get('guess_red_value', 0) * 100 / 115
    if guess_red_value:
        number_of_periods = int(timestamp_to_strftime(time.time() + 24 * 60 * 60, format='%Y%m%d')[2:]) * 1000
        for hour_int in range(24):
            hour_dict = red_hour_per_json.get(str(hour_int))
            per = hour_dict.get('per')
            # value = per * guess_red_value
            value = 24000
            while True:
                red_dict = reservation_hongbao(value, 12, 1000, 5)
                red_list = red_dict.get('red_list')
                if len(red_list) == 12:
                    break
            minute_int = 0
            for red_value in red_list:
                if red_value <= 1000:
                    red_value += random.randint(0, 1000)
                try:
                    timeArray = time.strptime('{0} {1}:{2}:00'.format(today_str, hour_int, minute_int),
                                              "%Y-%m-%d %H:%M:%S")
                    start_time = int(time.mktime(timeArray))
                    invalid_time = start_time + guess_red_invalid_time * 60

                    guess_red.insert_one({'today_str': today_str, 'hour_int': hour_int, 'minute_int': minute_int,
                                          'value': red_value, 'invalid_time': invalid_time, 'status': 0,
                                          'number_of_periods': number_of_periods + 1, 'start_time': start_time,
                                          'start_time_str': timestamp_to_strftime(start_time, format='%Y-%m-%d %H:%M')})
                    minute_int += 5
                    number_of_periods += 1
                except:
                    pass


def calculate_planet(operation_obj, user_obj, real_value, is_commission=True):
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
                                                  'origin': u'系统热量分红获得{0}元'.format(
                                                      '%.2f' % (float(real_value) / float(100))),
                                                  'value': int(commission_1),
                                                  'balance': int(commission_1 + planet_balance),
                                                  'user_id': invite_id, 'user_name': user_obj.get('nickname'),
                                                  'contributor_id': str(user_obj.get('_id')), 'is_arrival': 1,
                                                  'user_img': user_obj.get('headimgurl'), 'grade': 2, 'type_num': 4,
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
                                                  'origin': u'系统热量分红获得{0}元'.format(
                                                      '%.2f' % (float(real_value) / float(100))),
                                                  'value': int(commission_2),
                                                  'balance': int(commission_2 + planet_balance),
                                                  'user_id': superior_invite_id, 'user_name': user_obj.get('nickname'),
                                                  'contributor_id': str(user_obj.get('_id')), 'is_arrival': 1,
                                                  'user_img': user_obj.get('headimgurl'), 'grade': 3, 'type_num': 4,
                                                  'today': datetime.now().strftime(format='%Y-%m-%d'),
                                                  'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
                    if commission_record.find(
                            {'planet_id': superior_invite_id, 'type_num': 0, 'grade': 3}).count() == 1:
                        redis_invite_code.lpush('invite_json',
                                                json.dumps({'is_bind': 10, 'invite_id': superior_invite_id, 'grade': 3,
                                                            'value': '%.2f' % (float(commission_2) / float(100)) + u'元',
                                                            'nickname': u'附属居民' + user_obj.get('nickname')}))

    return real_value


def system_dividend():
    """
    系统分红
    :return:
    """
    dividend_calorific_total = 0
    operation_obj = operation.find_one()
    dividend_of_calorific = int(operation_obj.get('dividend_of_calorific', 2000))
    dividend_deduct_calorific_per = int(operation_obj.get('dividend_deduct_calorific_per', 80))
    penny_calorific = operation_obj.get('penny_calorific', 5)

    dividend_config_obj = dividend_config.find({}).sort([('today_str', -1)])[0]
    # 将分红金额转换为分 同时扣除15的上级分润
    dividend_value = int(dividend_config_obj.get('dividend_value', 0) * 100 * 100 / 115)
    user_cur = user.find({'available_calorific': {'$gt': dividend_of_calorific}, 'status': 0})
    for user_obj in user_cur:
        user_id = str(user_obj.get('_id'))
        available_calorific = user_obj.get('available_calorific')
        if available_calorific > dividend_of_calorific:
            participate_dividend_calorific = int(available_calorific * dividend_deduct_calorific_per / 100)
            dividend_calorific_total += participate_dividend_calorific
            redis_admin.lpush('system_dividend',
                              json.dumps({'participate_dividend_calorific': participate_dividend_calorific,
                                          'user_id': user_id}))

    while True:
        try:
            system_dividend_req = redis_admin.brpop('system_dividend', timeout=2)
            if not system_dividend_req:
                break
            system_dividend_dict = json.loads(system_dividend_req[1])
            user_id = system_dividend_dict.get('user_id')
            participate_dividend_calorific = system_dividend_dict.get('participate_dividend_calorific')

            try:
                user_obj = user.find_one({'_id': ObjectId(user_id)})
                if not user_obj:
                    continue
            except:
                continue

            value_total = int(participate_dividend_calorific / penny_calorific)
            user_dividend_value = int(value_total * 100 / 115)
            # user_dividend_value = int(dividend_value * participate_dividend_calorific / dividend_calorific_total)
            calorific_record.insert_one({'user_id': user_id, 'today': datetime.now().strftime(format='%Y-%m-%d'),
                                         'symbol': -1, 'type_num': 11, 'value': participate_dividend_calorific,
                                         'des': u'系统热量分红', 'red_id': '',
                                         'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})

            serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'), get_chars2(0, 1),
                                                           datetime.now().strftime(format='%m'), get_chars2(0, 1),
                                                           datetime.now().strftime(format='%d'), get_chars2(0, 1),
                                                           datetime.now().strftime(format='%H%M%S'))

            commission_record.insert_one({'serial_number': serial_number, 'planet_id': user_id,
                                          'origin': u'系统热量分红', 'value': int(user_dividend_value),
                                          'consume_calorific': participate_dividend_calorific, 'is_arrival': 1,
                                          'balance': int(user_dividend_value + user_obj.get('balance')),
                                          'user_id': user_id, 'user_name': user_obj.get('nickname'),
                                          'contributor_id': str(user_obj.get('_id')), 'type_num': 3,
                                          'user_img': user_obj.get('headimgurl'), 'grade': 1,
                                          'today': datetime.now().strftime(format='%Y-%m-%d'),
                                          'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
            user.update_one({'_id': user_obj.get('_id')},
                            {'$inc': {'planet_commission_total': user_dividend_value, 'balance': user_dividend_value,
                                      'available_calorific': -participate_dividend_calorific,
                                      'consumption_calorific': participate_dividend_calorific}})
            calculate_planet(operation_obj, user_obj, user_dividend_value)
        except:
            pass


if __name__ == '__main__':
    try:
        # 生成整点红包
        generate_integer_red()
    except Exception, e:
        print e
    try:
        # 生成猜红包的值
        generate_guess_red()
    except:
        pass
    time.sleep(29 * 60)
    try:
        # 系统分红
        system_dividend()
    except Exception, e:
        print e
