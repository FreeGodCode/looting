# -*- coding: utf8 -*-
# import sys
import time

from flask import Blueprint, jsonify, request

from libs.common import (login_api_check, judging_permissions)
from libs.db import (statistical_day, user, reg_user, commission_record, calorific_record, red_record, withdraw_record,
                     s_user_online_t, system, earth_code, ad_statistical_day, statistical_day_official,
                     integer_red_detail, guess_red_detail)
from libs.utils import timestamp_to_strftime

# reload(sys)
# sys.setdefaultencoding('utf-8')

statistical_api_blue = Blueprint('statistical_api', __name__, url_prefix='/api/statistical')


@statistical_api_blue.route('/my_list', methods=['get'])
@login_api_check()
def my_list():
    criteria = {}
    # 支持表格字段里的任何搜索
    access_status = judging_permissions('3_4_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)

    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = statistical_day.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        if page_num == 0:
            today_str = timestamp_to_strftime(int(time.time()), format='%Y-%m-%d')
            user_num_total = user.find({}).count()

            user_num = user.find({'created_time': {'$regex': today_str}}).count()
            user_num_active = s_user_online_t.find({'today_str': today_str}).count()
            integer_red_user_id_list = integer_red_detail.find({'today_str': today_str}).distinct('user_id')
            integer_red_user_num = len(integer_red_user_id_list)
            guess_red_user_id_list = guess_red_detail.find({'guess_time': {'$regex': today_str}}).distinct(
                'user_id')
            guess_red_user_num = len(guess_red_user_id_list)

            dict_obj = dict()

            real_user_num_active = user_num_active - user_num
            real_user_num_total = user_num_total - user_num
            dict_obj['today_str'] = today_str
            dict_obj['user_num_total'] = user_num_total
            dict_obj['user_num'] = user_num
            dict_obj['user_num_active'] = user_num_active
            dict_obj['real_user_num_active'] = real_user_num_active
            dict_obj['real_user_num_total'] = real_user_num_total
            dict_obj['user_num_active_per'] = '%.2f' % (
                    float(real_user_num_active * 100) / float(real_user_num_total)) + '%'

            dict_obj['integer_red_user_num'] = integer_red_user_num
            dict_obj['guess_red_user_num'] = guess_red_user_num
            dict_obj['integer_red_user_per'] = '%.2f' % (
                    float(integer_red_user_num * 100) / float(user_num_active)) + '%'
            dict_obj['guess_red_user_per'] = '%.2f' % (
                    float(guess_red_user_num * 100) / float(user_num_active)) + '%'
            _list.append(dict_obj)
            cur_list = _cur.sort([('today_str', -1)]).skip(page_num * limit).limit(limit)
        else:
            cur_list = _cur.sort([('today_str', -1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                user_num_total = _obj.get('user_num_total')
                user_num = _obj.get('user_num')
                user_num_active = _obj.get('user_num_active')
                real_user_num_active = user_num_active - user_num
                real_user_num_total = user_num_total - user_num
                _obj['real_user_num_active'] = real_user_num_active
                _obj['real_user_num_total'] = real_user_num_total
                _obj['user_num_active_per'] = '%.2f' % (
                        float(real_user_num_active * 100) / float(real_user_num_total)) + '%'
                _obj['integer_red_user_per'] = '%.2f' % (
                        float(_obj.get('integer_red_user_num', 0) * 100) / float(user_num_active)) + '%'
                _obj['guess_red_user_per'] = '%.2f' % (
                        float(_obj.get('guess_red_user_num', 0) * 100) / float(user_num_active)) + '%'
                _list.append(_obj)
            except Exception as e:
                print(e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@statistical_api_blue.route('/get_planet_day', methods=['get'])
@login_api_check()
def get_planet_day():
    access_status = judging_permissions('3_0_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    yesterday_str = timestamp_to_strftime(int(time.time()), format='%Y-%m-%d')

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
    statistical_day_obj = {
        'today_str': yesterday_str,
        'planet_num': user.find({'planet_id': {'$ne': ''}}).count(),
        'planet_commission': int(planet_commission / 100),
        'planet_commission_total': int(planet_commission_total / 100)
    }
    date_list = []
    planet_num_list = []
    planet_commission_list = []
    planet_commission_total_list = []
    date_list.insert(0, statistical_day_obj.get('today_str'))
    planet_num_list.insert(0, statistical_day_obj.get('planet_num'))
    planet_commission_list.insert(0, statistical_day_obj.get('planet_commission'))
    planet_commission_total_list.insert(0, int(planet_commission_total / 100))

    statistical_day_cur = statistical_day.find().sort([('today_str', -1)]).limit(29)

    for statistical_day_obj in statistical_day_cur:
        date_list.insert(0, statistical_day_obj.get('today_str'))
        planet_num_list.insert(0, statistical_day_obj.get('planet_num'))
        planet_commission_list.insert(0, int(statistical_day_obj.get('planet_commission') / 100))
        planet_commission_total_list.insert(0, int(statistical_day_obj.get('planet_commission_total', 0) / 100))
    return jsonify({'code': 200,
                    'data': {'date_list': date_list, 'planet_num_list': planet_num_list,
                             'planet_commission_list': planet_commission_list,
                             'planet_commission_total_list': planet_commission_total_list}})


@statistical_api_blue.route('/get_user_day', methods=['get'])
@login_api_check()
def get_user_day():
    access_status = judging_permissions('3_1_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    yesterday_str = timestamp_to_strftime(int(time.time()), format='%Y-%m-%d')

    earth_code_list = earth_code.find({}).distinct('invite_code')
    earth_code_list.append('')
    user_num_invite = user.find({'created_time': {'$regex': yesterday_str},
                                 'invite_id': {'$nin': earth_code_list}, }).count()
    user_red_record = len(red_record.find({'today': yesterday_str}).distinct('user_id'))

    statistical_day_obj = {
        'today_str': yesterday_str,
        'user_num_total': user.find({}).count(),
        'user_num': user.find({'created_time': {'$regex': yesterday_str}}).count(),
        'user_num_novice_task': user.find({'created_time': {'$regex': yesterday_str}, 'new_value': -1}).count(),
        'user_num_invite': user_num_invite,
        'user_num_invite_bind': reg_user.find({'today': yesterday_str, 'is_bind': 1}).count(),
        'user_num_active': s_user_online_t.find({'today_str': yesterday_str}).count(),
        'user_red_record': user_red_record,

    }
    date_list = []

    user_num_total_list = []
    user_num_list = []
    user_num_novice_task_list = []
    user_num_invite_list = []
    user_num_invite_bind_list = []
    user_num_active_list = []
    user_red_record_list = []

    date_list.insert(0, statistical_day_obj.get('today_str'))

    user_num_total_list.insert(0, statistical_day_obj.get('user_num_total'))
    user_num_list.insert(0, statistical_day_obj.get('user_num'))
    user_num_novice_task_list.insert(0, statistical_day_obj.get('user_num_novice_task'))
    user_num_invite_list.insert(0, statistical_day_obj.get('user_num_invite'))
    user_num_invite_bind_list.insert(0, statistical_day_obj.get('user_num_invite_bind'))
    user_num_active_list.insert(0, statistical_day_obj.get('user_num_active'))
    user_red_record_list.insert(0, statistical_day_obj.get('user_red_record'))

    statistical_day_cur = statistical_day.find().sort([('today_str', -1)]).limit(29)

    for statistical_day_obj in statistical_day_cur:
        date_list.insert(0, statistical_day_obj.get('today_str'))
        user_num_total_list.insert(0, statistical_day_obj.get('user_num_total'))
        user_num_list.insert(0, statistical_day_obj.get('user_num'))
        user_num_novice_task_list.insert(0, statistical_day_obj.get('user_num_novice_task'))
        user_num_invite_list.insert(0, statistical_day_obj.get('user_num_invite'))
        user_num_invite_bind_list.insert(0, statistical_day_obj.get('user_num_invite_bind'))
        user_num_active_list.insert(0, statistical_day_obj.get('user_num_active'))
        user_red_record_list.insert(0, statistical_day_obj.get('user_red_record'))

    return jsonify({'code': 200, 'data': {'date_list': date_list, 'user_num_total_list': user_num_total_list,
                                          'user_num_list': user_num_list,
                                          'user_num_novice_task_list': user_num_novice_task_list,
                                          'user_num_invite_list': user_num_invite_list,
                                          'user_num_invite_bind_list': user_num_invite_bind_list,
                                          'user_num_active_list': user_num_active_list,
                                          'user_red_record_list': user_red_record_list}})


@statistical_api_blue.route('/get_heat_day', methods=['get'])
@login_api_check()
def get_heat_day():
    access_status = judging_permissions('3_2_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    yesterday_str = timestamp_to_strftime(int(time.time()), format='%Y-%m-%d')

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
    statistical_day_obj = {
        'today_str': yesterday_str,

        'calorific_num_obtain': calorific_num_obtain,
        'calorific_num_expend': calorific_num_expend,
        'calorific_num': calorific_num,

    }
    date_list = []
    calorific_num_obtain_list = []
    calorific_num_expend_list = []
    calorific_num_list = []
    date_list.insert(0, statistical_day_obj.get('today_str'))
    calorific_num_obtain_list.insert(0, statistical_day_obj.get('calorific_num_obtain'))
    calorific_num_expend_list.insert(0, statistical_day_obj.get('calorific_num_expend'))
    calorific_num_list.insert(0, statistical_day_obj.get('calorific_num'))
    statistical_day_cur = statistical_day.find().sort([('today_str', -1)]).limit(29)
    for statistical_day_obj in statistical_day_cur:
        date_list.insert(0, statistical_day_obj.get('today_str'))
        calorific_num_obtain_list.insert(0, statistical_day_obj.get('calorific_num_obtain'))
        calorific_num_expend_list.insert(0, statistical_day_obj.get('calorific_num_expend'))
        calorific_num_list.insert(0, statistical_day_obj.get('calorific_num', 0))

    return jsonify({'code': 200, 'data': {'date_list': date_list,
                                          'calorific_num_obtain_list': calorific_num_obtain_list,
                                          'calorific_num_expend_list': calorific_num_expend_list,
                                          'calorific_num_list': calorific_num_list}})


@statistical_api_blue.route('/get_red_day', methods=['get'])
@login_api_check()
def get_red_day():
    access_status = judging_permissions('3_3_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    yesterday_str = timestamp_to_strftime(int(time.time()), format='%Y-%m-%d')

    red_record_num = red_record.find({'today': yesterday_str, 'type_num': {'$in': [2, 3]}}).count()
    user_red_record = len(red_record.find({'today': yesterday_str}).distinct('user_id'))
    red_average_num = '%.2f' % (float(red_record_num) / float(user_red_record))

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
    statistical_day_obj = {
        'today_str': yesterday_str,
        'red_num': int(red_num / 100),
        'user_balance_num': int(balance_total / 100),
        'withdraw_num': int(withdraw_total / 100),
        'red_record_num': red_record_num,
        'red_average_num': red_average_num
    }
    date_list = []

    red_num_list = []
    user_balance_num_list = []
    withdraw_num_list = []
    red_record_num_list = []
    red_average_num_list = []
    date_list.insert(0, statistical_day_obj.get('today_str'))
    red_num_list.insert(0, statistical_day_obj.get('red_num'))
    user_balance_num_list.insert(0, statistical_day_obj.get('user_balance_num'))
    red_record_num_list.insert(0, statistical_day_obj.get('red_record_num'))
    red_average_num_list.insert(0, statistical_day_obj.get('red_average_num'))
    withdraw_num_list.insert(0, statistical_day_obj.get('withdraw_num'))
    statistical_day_cur = statistical_day.find().sort([('today_str', -1)]).limit(29)

    for statistical_day_obj in statistical_day_cur:
        date_list.insert(0, statistical_day_obj.get('today_str'))
        red_num_list.insert(0, int(statistical_day_obj.get('red_num') / 100))
        user_balance_num_list.insert(0, int(statistical_day_obj.get('user_balance_num') / 100))
        withdraw_num_list.insert(0, int(statistical_day_obj.get('withdraw_num') / 100))
        red_record_num_list.insert(0, statistical_day_obj.get('red_record_num'))
        red_average_num_list.insert(0, float(statistical_day_obj.get('red_average_num')))

    return jsonify({'code': 200, 'data': {'date_list': date_list, 'red_num_list': red_num_list,
                                          'user_balance_num_list': user_balance_num_list,
                                          'withdraw_num_list': withdraw_num_list,
                                          'red_record_num_list': red_record_num_list,
                                          'red_average_num_list': red_average_num_list}})


@statistical_api_blue.route('/ad_list', methods=['get'])
@login_api_check()
def ad_list():
    criteria = {}
    # # 支持表格字段里的任何搜索
    # access_status = judging_permissions('4_4_3')
    # if access_status.get('code') != 200:
    #     return jsonify(access_status)

    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = ad_statistical_day.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('today_str', -1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])

                _list.append(_obj)
            except Exception as e:
                print(e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@statistical_api_blue.route('/user_share_list', methods=['get'])
@login_api_check()
def user_share_list():
    criteria = {}

    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = statistical_day.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('today_str', -1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                _list.append(_obj)
            except Exception as e:
                print(e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})


@statistical_api_blue.route('/statistical_official_invite', methods=['get'])
@login_api_check()
def statistical_official_invite():
    criteria = {}
    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})
    invite_code = request.args.get('invite_code', '')
    if invite_code:
        criteria.update({'invite_code': invite_code})
    _cur = statistical_day_official.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('today_str', -1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                total_invitation_num = _obj.get('total_invitation_num', 0)
                _obj['fission_num'] = total_invitation_num - _obj.get('first_level_invitation_num', 0)
                _list.append(_obj)
            except Exception as e:
                print(e)
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})
