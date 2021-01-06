# -*- coding: utf8 -*-

import json
import sys
import time
from datetime import datetime, timedelta

import requests
from bson import ObjectId

from conf import conf, conf_ver
from libs.db import (redis_ip, user, invite_code_data, redis_task2_code, redis_invite_code, operation,
                     calorific_record, error_log, redis_req_log, deviant_log, commission_record, earth_code, system,
                     cash_code_data, withdraw_record, integer_red_detail, guess_red_detail, guess_red, flash_sale,
                     configs, CONFIG_TYPE_FLASH_SALE)
from libs.utils import (random_str, generate_dwz, get_chars2, push_template, builder_random, unix_time_to_string,
                        get_now_part)


# reload(sys)
# sys.setdefaultencoding('utf-8')


def invite_return_calorific():
    """
    正常邀请奖现金奖热量
    :return:
    """
    req_number = 0
    while True:
        try:
            req_invite = redis_invite_code.brpop('invite_json', timeout=2)
            if not req_invite:
                if req_number < 50:
                    req_number += 2
                    continue
                else:
                    break
            req_number += 1
            invite_json = json.loads(req_invite[1])
            invite_id = invite_json.get('invite_id', '')
            is_bind = invite_json.get('is_bind', 0)
            user_id = invite_json.get('user_id', '')
            operation_obj = operation.find_one()
            effective_invitation_num = operation_obj.get('effective_invitation_num')
            calorific_number_people = operation_obj.get('calorific_number_people')
            effective_invitation_calorific = operation_obj.get('effective_invitation_calorific')
            effective_invitation_cash1 = operation_obj.get('effective_invitation_cash1')
            effective_invitation_cash2 = operation_obj.get('effective_invitation_cash2')
            # today_str = datetime.now().strftime(format='%Y-%m-%d')
            today_str = datetime.now().strftime('%Y-%m-%d')
            try:
                invite_user_obj = user.find_one({'_id': ObjectId(invite_id)})
            except:
                if is_bind == 1:
                    system.update_one({},
                                      {'$inc': {'planet_commission_total': effective_invitation_cash1}})
                if is_bind == 2:
                    system.update_one({},
                                      {'$inc': {'planet_commission_total': effective_invitation_cash2}})
                continue
            if is_bind == 10:
                # 第一笔分润通知
                grade = invite_json.get('grade')
                if commission_record.find({'planet_id': invite_id, 'type_num': 0, 'grade': grade}).count() == 1:
                    openid = invite_user_obj.get('wx_uid')
                    if conf_ver == 'conf.ProductionConfig':
                        template_id = 'kLvKUoi6_y_rB4CN1MBt3956Gh54_AkfxzItmH6yQtA'
                    else:
                        template_id = 'CuRkLGY-RCH-CZfxHnuQXEmAqm7Q1tvcDXJSwWUV0NY'

                    if openid:
                        try:
                            push_template(openid, template_id, '', invite_json.get('value', ''),
                                          u'您的{0}为您贡献了一笔分润，请进入热量星球APP查看我的收益。'.format(invite_json.get('nickname')),
                                          datetime.now().strftime('%Y-%m-%d %H:%M'))
                        except:
                            pass
                continue

            try:
                user_obj = user.find_one({'_id': ObjectId(user_id)})
            except:
                user_obj = dict()

            # 当用户初次绑定邀请码 给邀请人奖励0.3元
            commission_record_num = commission_record.find({'user_id': invite_id, 'today': today_str,
                                                            'type_num': 1, 'origin': u'邀请用户首次注册'}).count()
            if is_bind == 1 and commission_record_num < int(calorific_number_people):
                serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%m'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%d'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%H%M%S'))
                commission_record.insert_one({'serial_number': serial_number, 'planet_id': invite_id,
                                              'origin': u'邀请用户首次注册', 'is_arrival': 1,
                                              'value': int(effective_invitation_cash1),
                                              'balance': int(
                                                  effective_invitation_cash1 + invite_user_obj.get('balance')),
                                              'user_id': invite_id, 'user_name': user_obj.get('nickname'),
                                              'contributor_id': str(user_obj.get('_id')), 'type_num': 1,
                                              'user_img': user_obj.get('headimgurl'), 'grade': 2, 'today': today_str,
                                              'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})
                user.update_one({'_id': invite_user_obj.get('_id')},
                                {'$inc': {'planet_commission_total': effective_invitation_cash1,
                                          'balance': effective_invitation_cash1}})

            # 当用户首次提现  给邀请人返热量
            commission_record_num = commission_record.find({'user_id': invite_id, 'today': today_str,
                                                            'type_num': 1, 'origin': u'邀请用户首次提现'}).count()
            if is_bind == 2 and commission_record_num < int(calorific_number_people):
                serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%m'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%d'), get_chars2(0, 1),
                                                               datetime.now().strftime(format='%H%M%S'))
                commission_record.insert_one({'serial_number': serial_number, 'planet_id': invite_id,
                                              'origin': u'邀请用户首次提现', 'is_arrival': 1,
                                              'value': int(effective_invitation_cash2),
                                              'balance': int(
                                                  effective_invitation_cash2 + invite_user_obj.get('balance')),
                                              'user_id': invite_id, 'user_name': user_obj.get('nickname'),
                                              'contributor_id': str(user_obj.get('_id')), 'type_num': 1,
                                              'user_img': user_obj.get('headimgurl'), 'grade': 2, 'today': today_str,
                                              'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})

                calorific_record_dict = {'user_id': invite_id, 'today': today_str, 'symbol': 1,
                                         'type_num': 7, 'value': effective_invitation_calorific, 'des': u'邀请用户首次提现',
                                         'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}
                calorific_record.insert_one(calorific_record_dict)
                user.update_one({'_id': invite_user_obj.get('_id')},
                                {'$inc': {'planet_commission_total': effective_invitation_cash2,
                                          'balance': effective_invitation_cash2,
                                          'calorific_total': effective_invitation_calorific,
                                          'available_calorific': effective_invitation_calorific}})

            # 判断此邀请人数 看是否升级成了球主
            invite_user_obj = user.find_one({'_id': ObjectId(invite_id)})
            planet_id = invite_user_obj.get('planet_id', '')
            invite_user_num = user.find({'invite_id': invite_id, 'new_value': -1}).count()
            if invite_user_num >= effective_invitation_num and not planet_id:
                user.update_one({'_id': ObjectId(invite_id)}, {'$set': {'planet_id': invite_id}})
                # title = u'成为星主'
                # content = u'恭喜您达到系统要求的邀请人数，我们已经为您创建属于您自己的星球'
                # alert = {
                #     'title': title,
                #     'body': content
                # }
                # try:
                #     jp_notification(alert, title, 'id', '', type_num=1, jg_ids=[invite_user_obj.get('jg_id')])
                # except:
                #     pass
                # if conf_ver == 'conf.ProductionConfig':
                #     template_id = 'BicMMuwBiTojbCEGRocNevHJfYhibNYBHP_ieScf7KI'
                # else:
                #     template_id = '18IjSoLlT_ejZBhnpZrFq5tZeDMInBFCpG09qzw56Pc'
                # openid = invite_user_obj.get('wx_uid')
                # if openid:
                #     try:
                #         push_template(openid, template_id, '', invite_user_obj.get('name', ''),
                #                       invite_user_obj.get('phone', ''), '')
                #     except:
                #         pass
                # params_163 = '{}'
                # send_sms_163(invite_user_obj.get('phone'), params_163, '10858')

            # 如果邀请人成为球主 则同步其所有邀请人的球主信息
            invite_user_obj = user.find_one({'_id': ObjectId(invite_id)})
            planet_id = invite_user_obj.get('planet_id', '')
            if planet_id and invite_user_num < 30:
                # planet_commission_dict = commission_record.aggregate([
                #     {
                #         '$match': {'planet_id': planet_id, 'is_arrival': 0}
                #     },
                #     {
                #         '$group': {'_id': '', 'planet_commission': {'$sum': '$value'}}
                #     },
                #     {'$limit': 1}
                # ])
                # try:
                #     if isinstance(planet_commission_dict, dict):
                #
                #         _planet_commission_dict = planet_commission_dict.get('result')[0]
                #         planet_commission = int(_planet_commission_dict.get('planet_commission'))
                #     else:
                #         _planet_commission_dict = planet_commission_dict.next()
                #         planet_commission = int(_planet_commission_dict.get('planet_commission'))
                # except:
                #     planet_commission = 0
                # if planet_commission:
                #     user.update_one({'_id': ObjectId(planet_id)},
                #                     {'$inc': {'planet_commission_total': planet_commission,
                #                               'balance': planet_commission}})
                #     commission_record.update_many({'planet_id': planet_id, 'is_arrival': 0},
                #                                   {'$set': {'is_arrival': 1}})

                user.update_many({'invite_id': invite_id}, {'$set': {'superior_planet_id': planet_id}})
                user.update_many({'superior_invite_id': invite_id},
                                 {'$set': {'upperlevel_planet_id': planet_id}})
        except Exception as e:
            error_log.insert_one(
                {'fn_name': 'invite_return_calorific_1', 'invite_json': invite_json, 'error_str': str(e),
                 'today': datetime.now().strftime(format='%Y-%m-%d')})


def invite_activity_cash():
    """
    活动邀请奖现金奖
    :return:
    """

    req_number = 0
    while True:
        try:
            req_invite = redis_invite_code.brpop('invite_activity', timeout=2)
            if not req_invite:
                if req_number < 50:
                    req_number += 2
                    continue
                else:
                    break
            req_number += 1
            invite_json = json.loads(req_invite[1])

            invite_id = invite_json.get('invite_id', '')
            _type = invite_json.get('type', 1)
            user_id = invite_json.get('user_id', '')

            today_str = datetime.now().strftime(format='%Y-%m-%d')
            try:
                invite_user_obj = user.find_one({'_id': ObjectId(invite_id)})
                user_obj = user.find_one({'_id': ObjectId(user_id)})
            except:
                continue
            invite_active_status = user_obj.get('invite_active_status')

            user_input_time = user_obj.get('created_time').split(' ')[0]
            timeArray = time.strptime(user_input_time, "%Y-%m-%d")
            timeStamp = int(time.mktime(timeArray))
            effective_time = unix_time_to_string(unix_time=timeStamp + 6 * 24 * 60 * 60, format='%Y-%m-%d')
            if effective_time < today_str:
                if invite_active_status in [-1, -2]:
                    continue
                user.update_one({'_id': user_obj.get('_id')}, {'$set': {'invite_active_status': -2}})
            invite_active_time = user_obj.get('invite_active_time')
            if invite_active_time == today_str:
                continue
            if _type == 1:
                if invite_active_status != 0:
                    continue
                if withdraw_record.find({'user_id': user_id, 'status': 1}).count() > 0:
                    invite_active_complete_num = user.find({'invite_id': invite_id, 'invite_active_status': -1}).count()
                    if invite_active_complete_num < 318:
                        serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%m'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%d'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%H%M%S'))
                        commission_record.insert_one({'serial_number': serial_number, 'planet_id': invite_id,
                                                      'origin': u'活动邀请用户提现', 'is_arrival': 1, 'value': 20,
                                                      'balance': int(20 + invite_user_obj.get('balance')),
                                                      'user_id': invite_id, 'user_name': user_obj.get('nickname'),
                                                      'contributor_id': str(user_obj.get('_id')), 'type_num': 2,
                                                      'user_img': user_obj.get('headimgurl'), 'grade': 2,
                                                      'today': today_str,
                                                      'created_time': datetime.now().strftime(
                                                          format='%Y-%m-%d %H:%M:%S')})
                        user.update_one({'_id': invite_user_obj.get('_id')},
                                        {'$inc': {'planet_commission_total': 20, 'balance': 20}})
                        user.update_one({'_id': user_obj.get('_id')},
                                        {'$set': {'invite_active_status': 1, 'invite_active_time': today_str},
                                         '$inc': {'invite_active_cash': 20}})
                    else:
                        user.update_one({'_id': user_obj.get('_id')},
                                        {'$set': {'invite_active_status': -2, 'invite_active_time': today_str}})
            else:
                if invite_active_status in [1, 2]:
                    invite_active_complete_num = user.find({'invite_id': invite_id, 'invite_active_status': -1}).count()
                    if invite_active_complete_num < 318:
                        serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%m'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%d'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%H%M%S'))
                        commission_record.insert_one({'serial_number': serial_number, 'planet_id': invite_id,
                                                      'origin': u'活动邀请用户完成第二天抢红包', 'is_arrival': 1, 'value': 30,
                                                      'balance': int(30 + invite_user_obj.get('balance')),
                                                      'user_id': invite_id, 'user_name': user_obj.get('nickname'),
                                                      'contributor_id': str(user_obj.get('_id')), 'type_num': 2,
                                                      'user_img': user_obj.get('headimgurl'), 'grade': 2,
                                                      'today': today_str,
                                                      'created_time': datetime.now().strftime(
                                                          format='%Y-%m-%d %H:%M:%S')})
                        user.update_one({'_id': invite_user_obj.get('_id')},
                                        {'$inc': {'planet_commission_total': 30, 'balance': 30}})
                        user.update_one({'_id': user_obj.get('_id')},
                                        {'$set': {'invite_active_status': 3, 'invite_active_time': today_str},
                                         '$inc': {'invite_active_cash': 30}})
                    else:
                        user.update_one({'_id': user_obj.get('_id')},
                                        {'$set': {'invite_active_status': -2, 'invite_active_time': today_str}})
                elif invite_active_status in [3, 4]:
                    invite_active_complete_num = user.find({'invite_id': invite_id, 'invite_active_status': -1}).count()
                    if invite_active_complete_num < 318:
                        integer_red_detail_count = integer_red_detail.find({'today_str': today_str,
                                                                            'user_id': user_id}).count()
                        guess_red_detail_count = guess_red_detail.find({'guess_time': {'$regex': today_str},
                                                                        'user_id': user_id}).count()
                        if (integer_red_detail_count + guess_red_detail_count) < 2:
                            continue
                        if invite_active_complete_num >= 200:
                            cash_value = 200
                        elif invite_active_complete_num >= 100:
                            cash_value = 150
                        elif invite_active_complete_num >= 20:
                            cash_value = 130
                        elif invite_active_complete_num >= 3:
                            cash_value = 100
                        else:
                            cash_value = 50

                        serial_number = '{0}{1}{2}{3}{4}{5}{6}'.format(datetime.now().strftime(format='%Y'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%m'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%d'),
                                                                       get_chars2(0, 1),
                                                                       datetime.now().strftime(format='%H%M%S'))
                        commission_record.insert_one({'serial_number': serial_number, 'planet_id': invite_id,
                                                      'origin': u'活动邀请用户完成第三天抢两红包', 'is_arrival': 1,
                                                      'value': cash_value,
                                                      'balance': int(cash_value + invite_user_obj.get('balance')),
                                                      'user_id': invite_id, 'user_name': user_obj.get('nickname'),
                                                      'contributor_id': str(user_obj.get('_id')), 'type_num': 2,
                                                      'user_img': user_obj.get('headimgurl'), 'grade': 2,
                                                      'today': today_str,
                                                      'created_time': datetime.now().strftime(
                                                          format='%Y-%m-%d %H:%M:%S')})
                        user.update_one({'_id': invite_user_obj.get('_id')},
                                        {'$inc': {'planet_commission_total': cash_value, 'balance': cash_value}})
                        user.update_one({'_id': user_obj.get('_id')},
                                        {'$set': {'invite_active_status': -1, 'invite_active_time': today_str},
                                         '$inc': {'invite_active_cash': cash_value}})
                    else:
                        user.update_one({'_id': user_obj.get('_id')},
                                        {'$set': {'invite_active_status': -2, 'invite_active_time': today_str}})
                else:
                    continue
        except Exception as e:
            error_log.insert_one(
                {'fn_name': 'invite_return_calorific_1', 'invite_activity': invite_json, 'error_str': str(e),
                 'today': datetime.now().strftime(format='%Y-%m-%d')})


def generate_invite_code():
    """
    生成邀请码
    :return:
    """
    if invite_code_data.find({'status': 0}).count() < 15000:
        for i in range(1000):
            invite_code = random_str(5)
            invite_code_obj = invite_code_data.find_one({'invite_code': invite_code})
            user_obj = user.find_one({'invite_code': invite_code})
            earth_code_obj = earth_code.find_one({'invite_code': invite_code})
            if not invite_code_obj and not user_obj and not earth_code_obj:
                invite_url_short = ''
                if conf_ver == 'conf.ProductionConfig':
                    invite_url_short = generate_dwz(
                        '{0}/h5/reg?invite_code={1}&source=invite'.format(conf.api_url, invite_code))
                    if not invite_url_short:
                        continue
                else:
                    invite_url_short = '{0}/h5/reg?invite_code={1}&source=invite'.format(conf.api_url, invite_code)
                invite_code_data.insert_one(
                    {'invite_code': invite_code, 'status': 0, 'invite_url_short': invite_url_short})


def send_invite_code():
    """
     发送邀请码任务
    :return:
    """
    invite_code_len = redis_invite_code.llen('invite_code')
    if invite_code_len < 10000:
        invite_code_data_cur = invite_code_data.find({'status': 0}).limit(100)
        for invite_code_data_obj in invite_code_data_cur:
            invite_code_data.update_one({'_id': invite_code_data_obj.get('_id')}, {'$set': {'status': 1}})
            redis_invite_code.lpush('invite_code', invite_code_data_obj.get('invite_code'))


def generate_cash_code():
    """
    生成 关注公众号 的提现码
    :return:
    """
    if cash_code_data.find({'status': 0}).count() < 100000:
        for i in range(1000):
            cash_code = builder_random(6)
            cash_code_obj = cash_code_data.find_one({'code': cash_code})
            if not cash_code_obj:
                cash_code_data.insert_one({'code': cash_code, 'status': 0,
                                           'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})


def send_cash_code():
    """
     发送关注公众号 提现码的任务
    :return:
    """
    cash_code_len = redis_task2_code.llen('cash_code')
    if cash_code_len < 10000:
        cash_code_data_cur = cash_code_data.find({'status': 0}).limit(100)
        for cash_code_data_obj in cash_code_data_cur:
            cash_code_data.update_one({'_id': cash_code_data_obj.get('_id')}, {'$set': {'status': 1}})
            redis_task2_code.lpush('cash_code', cash_code_data_obj.get('code'))


def get_proxy_ip_new():
    """
    生成代理ip
    :return:
    """
    if redis_ip.llen('normal') > 10000:
        return None
    url = 'http://tvp.daxiangdaili.com/ip/?tid=558934365661740&num=1000&category=2&foreign=none'
    res = requests.get(url, timeout=10)
    if res.status_code != 200:
        print(u'获取代理IP失败……')
        time.sleep(2)
        url = 'http://tvp.daxiangdaili.com/ip/?tid=558934365661740&num=1000&category=2&foreign=none'
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print(u'获取代理IP失败……')
            return
    ips = res.text.splitlines()
    for ip in ips:
        if ip.find('ERROR') > -1:
            print(u'跳过')
            continue
        print(ip)
        ip = ip.strip()
        redis_ip.lpush('normal', ip)
    return True


def insert_error_log():
    """
    插入服务器错误请求日志
    :return:
    """
    req_number = 0
    while True:
        req_number += 1
        error_log_array = redis_req_log.brpop('error_log', timeout=2)
        if not error_log_array:
            if req_number < 60:
                req_number += 2
                time.sleep(1)
                continue
            else:
                break
        error_log_json = json.loads(error_log_array[1])
        # todo 做一些 数据统计
        error_log.insert_one(error_log_json)


def insert_deviant_log():
    """
    插入异常请求日志
    :return:
    """
    while True:
        deviant_log_array = redis_req_log.brpop('deviant_log', timeout=2)
        if not deviant_log_array:
            break
        deviant_log_json = json.loads(deviant_log_array[1])
        # todo 做一些 数据统计
        deviant_log.insert_one(deviant_log_json)


def update_guess_red_status():
    now_time = int(time.time())
    guess_red_cur = guess_red.find({'status': 0, 'invalid_time': {'$lt': now_time}})
    for guess_red_obj in guess_red_cur:
        guess_red.update_one({'_id': guess_red_obj.get('_id')}, {'$set': {'status': -1}})


def open_flash_sale():
    now = datetime.now()
    now_date = get_now_part('%Y-%m-%d')
    config_obj = configs.find_one({'type_num': CONFIG_TYPE_FLASH_SALE})
    if not config_obj:
        config_obj = {'hour_list': []}

    hour_list = config_obj['hour_list']
    if filter(lambda x: x == now.hour, hour_list):
        flash_sale.update_many({'date': now_date, 'hour': now.hour, 'status': 0}, {'$set': {'status': 1}})

    end_time = now - timedelta(hours=1)
    if end_time.hour == 23:
        now_date = now_date - timedelta(days=1)
    flash_sale.update_many({'date': now_date, 'hour': end_time.hour}, {'$set': {'status': 2}})


# 每一分钟执行一次的解本
if __name__ == '__main__':
    try:
        open_flash_sale()
    except Exception as e:
        print('open_flash_sale: ' + str(e))
    try:
        # 服务器内部错误日志处理
        insert_error_log()
    except Exception as e:
        print('insert_error_log: ' + str(e))
    try:
        # 插入异常请求日志
        insert_deviant_log()
    except Exception as e:
        print('insert_deviant_log: ' + str(e))
    try:
        # 定时生成邀请码
        generate_invite_code()
    except Exception as e:
        print('generate_invite_code: ' + str(e))
    try:
        # 将用户的邀请码 发送到消息队列任务
        send_invite_code()
    except Exception as e:
        print('send_invite_code: ' + str(e))
    # try:
    #     # 生成 关注公众号 的提现码
    #     generate_cash_code()
    # except Exception, e:
    #     print 'generate_cash_code: ' + str(e)

    # for i in range(100):
    #     # 生成代理ip
    #     try:
    #         get_proxy_value = get_proxy_ip_new()
    #         if not get_proxy_value:
    #             break
    #     except Exception, e:
    #         print 'get_proxy_ip_new: ' + str(e)
    #     time.sleep(2)
