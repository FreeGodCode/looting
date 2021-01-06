# -*- coding: utf8 -*-
import time
from datetime import datetime

from libs.db import withdraw_record, user, red_record, s_user_online_t

default_des = {
    'access_token': u'微信登录token',
    'refresh_token': u'刷新微信登录token',
    'openid': u'微信用户在此应用的唯一标识',
    'unionid': u'微信用户在此平台账号下的唯一标识',
    'nickname': u'用户昵称',
    'headimgurl': u'头像',
    'sex': u'性别',
    'province': u'省份',
    'city': u'城市',
    'country': u'国家',
    'intro': u'个人签名',
    'app_version': u'app版本号',
    'mp_system_type': u'用户手机系统',
    'mp_system_version': u'手机平台的系统版本，字符串类型',
    'mp_version': u'引擎版本信息，字符串类型',
    'mp_device_id': u'设备唯一标识，字符串类型',
    'mp_device_model': u'设备型号，字符串类型',
    'mp_device_name': u'设备名称，字符串类型',

    'name': u'真实姓名',
    'id_card': u'身份证号',
    'verified_status': u'认证状态',
    'birth_year': u'出生年',

    'wx_uid': u'微信提现绑定id',
    'al_uid': u'支付宝提现绑定id',

    'mobile': u'手机号',
    'invite_code': u'邀请码',
    'invite_ids': u'上级邀请人id列表',
    'invite_name': u'邀请人名称',
    'reg_source': u'注册来源',

    'status': u'用户状态',
    'login_times': u'登录次数',
    'last_login_times': u'最后登录时间',

    'withdraw_status': u'提现状态',
    'virtual_balance': u'账户可用奖券余额',
    'balance': u'账户可用余额',
    'red_total': u'抢到的红包总额',
    'alipay_name': u'支付宝账号真实姓名',
    'alipay_phone': u'支付宝账号',
    'alipay_account': u'支付宝账号',
    'weixin_qrcode': u'微信收款二维码',
    'jg_id': u'极光id',
    'invite_url_short': u'邀请短链接地址',
    'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')
}

default_values = {
    'access_token': u'',
    'refresh_token': u'',
    'openid': u'',
    'unionid': u'',
    'nickname': u'',
    'headimgurl': u'',
    'sex': 0,
    'province': u'',
    'city': u'',
    'country': u'',
    'intro': u'',
    'app_version': u'',
    'mp_system_type': u'',
    'mp_system_version': u'',
    'mp_version': u'',
    'mp_device_id': u'',
    'mp_device_model': u'',
    'mp_device_name': u'',

    'name': u'',
    'id_card': u'',
    'verified_status': 0,

    'wx_uid': u'',
    'al_uid': u'',

    'mobile': u'',
    'invite_code': u'',
    'invite_id': u'',
    'reg_source': u'',

    'status': 0,
    'login_times': 0,
    'last_login_times': u'',

    'virtual_balance': 0,
    'balance': 0,
    'red_total': 0,
    'alipay_name': u'',
    'alipay_phone': u'',
    'alipay_account': u'',
    'invite_url_short': u'',
    'withdraw_status': 0,
    'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')
}

sex_values = {
    0: u'未知',
    1: u'男',
    2: u'女'
}

status_values = {
    -1: u'封禁',
    0: u'正常'

}

verified_status_values = {
    -1: u'认证失败',
    0: u'未认证',
    1: u'认证通过',
}

withdraw_status_values = {
    -2: u'提现失败',
    -1: u'已提现',
    0: u'未提现',
    1: u'审核中'
}

int_keys = ['verified_status', 'status', 'sex', 'grade', 'showTimes', 'login_times',
           'withdraw_status']

if __name__ == '__main__':
    for i in range(117):
        user.insert_one({
            "headimgurl": "http://thirdwx.qlogo.cn/mmopen/vi_32/h5FrlQoFIQkHVAMPHPzBxcLI9hO33jegN3bdsMnVINshkkbeCG0Ek87vLs16q2uYymYRhOiaGQ2dU0xvabibRiafQ/132",
            "grade": 2,
            "withdraw_status": -1,
            "verified_status": 1,
            "mp_device_id": "A6B9EA12-F5BB-4ADD-8D4A-EE01D03DC196",
            "new_value": -1,
            "created_time": "2019-09-27 14:52:57",
            "mp_device_name": "iPhone",
            "last_login_times": "2019-09-27 14:52:57",
            "city": "",
            "mp_system_type": "ios",
            "nickname": "か",
            "id_card": "3707022003050822211",
            "jg_id": "1114a89792ca9a36a97",
            "app_version": "00.00.92",
            "available_calorific": 10,
            "invite_url_short": "",
            "planet_headimgurl": "https://static.yiqifu88.com/20190827192355-1r9z.jpg",
            "invite_active_cash": 250,
            "planet_commission_total": 0,
            "consumption_calorific": 100,
            "phone": "18671940555",
            "invite_active_status": -1,
            "name": "王雅静1",
            "access_token": "25_AoA2ljuRnYTG1X5_ALGsDp16AU0J_nEve45IQkcS5B-X6nGVOwySfnorxj4Wu6QlDTtUqv0L-LaubZcMxWdTkvxxdZyNEDsvWouiuNlXYTA",
            "invite_id": "5d8cbbe32b570000070d877c",
            "planet_red_total": 0,
            "superior_invite_id": "",
            "country": "YE",
            "superior_planet_id": "5d8cbbe32b570000070d877c",
            "balance": 596,
            "red_total": 626,
            "status": 0,
            "calorific_red_num": 0,
            "mp_device_model": "iPhone 7",
            "sex": 2,
            "intro": "",
            "login_times": 1,
            "wx_uid": "oWK1lvykpGGhES2yPVfH928DN_xs1",
            "invite_code": "dy906",
            "planet_id": "",
            "birth_year": "2003",
            "province": "",
            "openid": "oPqsks8e0wEYWyOxJdZ6SgzNX5TA1",
            "calorific_total": 110,
            "mp_system_version": "12.4.1",
            "planet_name": "か的星球",
            "upperlevel_planet_id": "",
            "mp_version": "1.3.27",
            "refresh_token": "25_MjxP2dVPGMtkhvquR2QwVSYFgzXXZCrG_qA-M2FBV8mr-DLTPr8tIy6IR1ZgB6HemMe88VECt-opX4D_KROaEuZdWPTmOdse63o8hqzUrJ0",
            "al_uid": "",
            "reg_source": "",
            "unionid": "oLaQOwsqwrwR6lOwKh2xgsghmqbc",
            "invite_active_time": "2019-09-27"})

    print (u'用户手机&&昵称&&从注册到提现耗时&&从注册到抢红包耗时&&余额&&已提现金额&&冻结金额&&活跃天数&&邀请人数&&邀请人&&拆红包次数&&注册时间')
    user_cur = user.find()
    for user_obj in user_cur:
        withdraw_time = 0
        created_time = user_obj.get('created_time')
        timeArray = time.strptime(created_time, "%Y-%m-%d %H:%M:%S")

        timeStamp = int(time.mktime(timeArray))
        withdraw_record_obj = withdraw_record.find_one({'user_id': str(user_obj.get('_id'))})
        if withdraw_record_obj:
            created_time = withdraw_record_obj.get('created_time')
            timeArray = time.strptime(created_time, "%Y-%m-%d %H:%M:%S")
            timeStamp2 = int(time.mktime(timeArray))

            withdraw_time = int(timeStamp2 - timeStamp) / 60
            if not withdraw_time:
                withdraw_time = 1
        red_time = 0
        red_record_obj = red_record.find_one({'user_id': str(user_obj.get('_id')), 'type_num': {'$in': [2, 3]}})
        if red_record_obj:
            created_time = red_record_obj.get('created_time')
            timeArray = time.strptime(created_time, "%Y-%m-%d %H:%M:%S")
            timeStamp1 = int(time.mktime(timeArray))
            red_time = int(timeStamp1 - timeStamp) / 60
            if not red_time:
                red_time = 1
        withdraw_total_dict = withdraw_record.aggregate([
            {
                '$match': {'user_id': str(user_obj.get('_id')), 'status': 1}
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
        withdraw_total_dict1 = withdraw_record.aggregate([
            {
                '$match': {'user_id': str(user_obj.get('_id')), 'status': 0}
            },
            {
                '$group': {'_id': '', 'withdraw_total': {'$sum': '$value'}}
            },
            {'$limit': 1}
        ])
        try:
            if isinstance(withdraw_total_dict1, dict):
                _withdraw_total_dict1 = withdraw_total_dict1.get('result')[0]
                withdraw_total1 = int(_withdraw_total_dict1.get('withdraw_total'))
            else:
                _withdraw_total_dict1 = withdraw_total_dict1.next()
                withdraw_total1 = int(_withdraw_total_dict1.get('withdraw_total'))
        except:
            withdraw_total1 = 0

        s_user_online_t_num = s_user_online_t.find({'user_id': str(user_obj.get('_id'))}).count()
        invite_num = user.find({'invite_id': str(user_obj.get('_id'))}).count()
        invite_name = u'无'
        if user_obj.get('invite_id'):
            try:
                user_obj['invite_name'] = user.find_one({'_id': user_obj.get('invite_id')}).get('nickname')
            except:
                invite_name = u'官方邀请'
        red_record_num = red_record.find({'user_id': str(user_obj.get('_id')),
                                          'type_num': {'$in': [2, 3]}}).count()
        print(u'{0}&&{1}&&{2}&&{3}&&{4}&&{5}&&{6}&&{7}&&{8}&&{9}&&{10}&&{11}'.format(
            user_obj.get('phone'),
            user_obj.get('nickname'),
            withdraw_time, red_time,
            '%.2f' % (float(user_obj.get('balance')) / 100),
            '%.2f' % (float(withdraw_total)/100),
            '%.2f' % (float(withdraw_total1)/100),
            s_user_online_t_num, invite_num,
            invite_name, red_record_num,
            user_obj.get('created_time')))
