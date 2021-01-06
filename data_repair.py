# -*- coding: utf8 -*-

import hashlib
import json
import time
import uuid

import requests
from bson import ObjectId

from libs.db import user, commission_record, operation, dividend_config, redis_admin
from libs.utils import timestamp_to_strftime


def repair_data():
    user_cur = user.find({})
    for user_obj in user_cur:
        planet_id = str(user_obj.get('_id'))
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
            print(planet_commission)
            user.update_one({'_id': ObjectId(planet_id)},
                            {'$inc': {'planet_commission_total': planet_commission,
                                      'balance': planet_commission}})
            commission_record.update_many({'planet_id': planet_id, 'is_arrival': 0},
                                          {'$set': {'is_arrival': 1}})


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
    user_dividend_value_total = 0
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
            user_dividend_value_total += user_dividend_value
            print(user_dividend_value, participate_dividend_calorific, user_id)
        except:
            pass
    print(user_dividend_value_total)


def third_transfer_profit():
    """
    :param os: 1为安卓，2为ios
    :param uid: 用户唯 一id
    :return:
    """
    yesterday_str = timestamp_to_strftime((int(time.time())), format='%Y-%m-%d')

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
                except Exception as e:
                    continue
            if json_data:
                ips = json_data.get('ips', 0)
                if ips:
                    print(user_id, ips)
        except:
            pass


if __name__ == '__main__':
    third_transfer_art_token = 'I68v0YUjdmmfrjUL75m0s5vgsZ4Zs40LI60ng19isHU68EsZI4tGzIUmty4ot5mE560EhGmUcktchE9h3ot7rmlXcGC0gy_ycncv71tlh6cYdlKm4mlOfg))'

    json_data = {}
    for i in range(3):
        try:
            ts = int(time.time() * 1000)
            uuid_m = hashlib.md5(str(uuid.uuid4()).replace('-', ''))
            opt = {'day': '2019-11-10', 'token': third_transfer_art_token, 'uuid': uuid_m.hexdigest(),
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
            print(req_json)
            if req_json.get('code') == 0 and req_json.get('data', {}):
                json_data = req_json.get('data', {})
                break
        except Exception as e:
            print(e)
            continue
