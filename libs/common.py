# -*- coding: utf-8 -*-
import hashlib
import json
import time
from datetime import datetime
from functools import wraps

import requests
from asynctools.threading import Async
from bson import ObjectId
from flask import request, session, render_template, jsonify

from Wecaht_red import paymkttransfers
from conf import conf_ver
from libs.alipay_transfer import Payment
from libs.crypt import XKcrypt
from libs.db import (admin_user, user_role, role_authority, redis_admin, redis_code, user, withdraw_record,
                     redis_invite_code, station_notice)
from libs.iptool import ip2region
from libs.utils import push_template, jp_notification

crypt_obj = XKcrypt()


def judging_permissions(authority):
    username = session.get('username')
    user_obj = admin_user.find_one({'username': username, 'status': 0})
    if not user_obj:
        return {'code': 230, 'msg': u'当前未登录，无法访问'}
    role_id_list = user_role.find({'user_id': str(user_obj.get('_id'))}).distinct('role_id')
    if role_authority.find_one({'role_id': {'$in': role_id_list}, 'authority': authority}):
        return {'code': 200, 'msg': u''}
    else:
        return {'code': 208, 'msg': u'您无此操作权限，如想操作请联系管理员'}


def get_request_params():
    """
    获取 http 请求的所有参数
    :return:
    """
    all_params = dict()
    if request.method == 'GET':
        # 获取所有get请求参数
        request_params = request.args.items()

        for param in request_params:
            all_params[param[0]] = param[1]
    else:
        # 获取所有post请求参数
        all_params = {key: dict(request.form)[key][0] for key in dict(request.form)}
        if not all_params:
            all_params = request.get_json()
    if not all_params:
        all_params = dict()
    return all_params


def get_ip_area(ip=None, is_area=True):
    """这是最新的ip -> region方法，通过查找离线库获取数据"""
    if not ip:
        try:
            ip = request.headers.get('X-Forwarded-For').split(',')[0]
        except:
            ip = request.remote_addr
    if is_area:
        ip_area = ip2region(ip)
        if not ip_area or '|' not in ip_area:
            ip_area = u'未知'
    else:
        ip_area = u'未知'
    return ip, ip_area


def login_check(fn):
    """
    登录检查
    :param fn:
    :return:
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):

        username = session.get('username')
        if not username:
            user_key = request.cookies.get('admin_key')
            if not user_key:
                # 因为后台采用的是ifrmae框架，未登录状态下通过js跳转可防止登录页面在iframe子页面中打开
                return render_template('jump.html')
            r_username = redis_admin.get(user_key)
            _username = crypt_obj.decrypt(user_key)
            real_username = _username.split('__')[0]
            if r_username != real_username:
                return render_template('jump.html')
            login_time = _username.split('__')[-1]
            try:
                login_time = int(login_time)
                login_jg = int(time.time()) - login_time
                if login_jg > 60 * 60 * 24:
                    return render_template('jump.html')
            except:
                return render_template('jump.html')
            username = r_username
        user_obj = admin_user.find_one({'username': username, 'status': 0})
        if not user_obj:
            return render_template('jump.html')
        session['username'] = username
        return fn(*args, **kwargs)

    return wrapper


def login_api_check(code_verif=False):
    """
    api登录检查

    :return:
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            username = session.get('username')
            if not username:
                user_key = request.cookies.get('admin_key')
                if not user_key:
                    # 如果未登录则重定向到登录页面
                    return jsonify({'code': 230, 'msg': u'当前未登录，无法访问'})
                r_username = redis_admin.get(user_key)
                _username = crypt_obj.decrypt(user_key)
                real_username = _username.split('__')[0]
                if r_username != real_username:
                    return jsonify({'code': 230, 'msg': u'当前未登录，无法访问'})
                login_time = _username.split('__')[-1]
                try:
                    login_time = int(login_time)
                    login_jg = int(time.time()) - login_time
                    if login_jg > 60 * 60 * 24:
                        return jsonify({'code': 230, 'msg': u'登录过期，请从新登录'})
                except:
                    return jsonify({'code': 230, 'msg': u'当前未登录，无法访问'})
                username = r_username
            user_obj = admin_user.find_one({'username': username, 'status': 0})
            if not user_obj:
                return jsonify({'code': 230, 'msg': u'当前未登录，无法访问'})
            if conf_ver == 'conf.ProductionConfig':
                if code_verif:
                    data = get_request_params()
                    input_phonecode = data.get('input_phonecode')
                    if redis_code.get(user_obj.get('phone')) != input_phonecode:
                        return jsonify({'code': 210, 'msg': u'短信验证码错误'})
            session['username'] = username
            session['real_name'] = user_obj.get('real_name', '')
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@Async
def failure_notification(openid, _obj, remark, user_obj):
    """
    提现失败通知
    :param openid:
    :param _obj:
    :param remark:
    :param user_obj:
    :return:
    """

    if conf_ver == 'conf.ProductionConfig':
        template_id = 'UknWg_f71WRhYNjm-dr4JPacykJX0ZkeXddphUtFcHc'
    else:
        template_id = '-FAS2kf4aKbhBkVndi-LO28t4EMVupH-eMOxkB1iCBM'
    if openid:
        push_template(openid, template_id, _obj.get('origin'),
                      '%.2f' % (float(_obj.get('value', 0)) / float(100)) + u'元', _obj.get('created_time')[: 16],
                      remark)
    title = u'提现失败'
    content = u'您的提现申请失败,失败原因为:{0}。'.format(remark)
    alert = {
        'title': title,
        'body': content
    }
    try:
        jp_notification(alert, title, 'id', '', type_num=1, jg_ids=[user_obj.get('jg_id')])
    except:
        pass


@Async
def successful_notification(openid, _obj, user_id, user_obj):
    """
    提现成功通知
    :param openid:
    :param _obj:
    :param user_id:
    :param user_obj:
    :return:
    """
    if conf_ver == 'conf.ProductionConfig':
        template_id = 'KNteD66yN8I3uL4ObD2jZJn3py74Uezn2WeImEFwkkI'
    else:
        template_id = 'wuVWd1zIgtki7iNGh5a3Dq-wQzKbPCdBjkptsEVz0GM'
    if openid:
        push_template(openid, template_id, _obj.get('origin'),
                      '%.2f' % (float(_obj.get('value', 0)) / float(100)) + u'元', '', '')
    title = u'提现成功'
    content = u'恭喜您提现审核通过成功提现 {0}元'.format('%.2f' % (float(_obj.get('value', 0)) / float(100)))
    alert = {
        'title': title,
        'body': content
    }
    try:
        jp_notification(alert, title, 'id', '', type_num=1, jg_ids=[user_obj.get('jg_id')])
    except:
        pass


def get_sign_params(opt, sing_key='sign'):
    """
    获取加密串

    :param opt: 加密参数
    :return: 一个 MD5 值
    """
    if not opt or not isinstance(opt, dict):
        return ''
    if sing_key in opt:
        del opt[sing_key]
    key_az = sorted(opt.keys())
    pair_array = []
    for k in key_az:
        v = str(opt.get(k, '')).strip()
        if not v:
            continue
        try:
            k = k.encode('utf8')
            v = v.encode('utf8')
        except:
            k = k.decode('ascii').encode('utf8')
            v = v.decode("ascii").encode('utf8')
        pair_array.append('%s=%s' % (k, v))
    tmp = '&'.join(pair_array)
    # 将所有的值进行拼接，包括加密串
    result_old = tmp + '&secret_key=FA77E2804734C22F72B22D9B7EDB41A9'
    m = hashlib.md5(result_old)
    md5_text = m.hexdigest()

    return md5_text


def withdraw_way(serial_number, automatic_withdraw_cash=20000, is_back=True, review_name=u'系统自动'):
    withdraw_record_obj = withdraw_record.find_one({'serial_number': serial_number})
    origin = withdraw_record_obj.get('origin')
    value = withdraw_record_obj.get('value')
    user_id = withdraw_record_obj.get('user_id', '')
    user_obj = user.find_one({'_id': ObjectId(user_id)})
    balance = user_obj.get('balance')
    if not is_back:
        if balance < value:
            withdraw_record.update_one({'serial_number': serial_number}, {'$set': {'status': -2}})
            return False
        user.update_one({'_id': ObjectId(user_id)}, {'$inc': {'balance': -value}})
        if value <= automatic_withdraw_cash:
            if origin == u'微信提现':
                if user_obj.get('wx_uid', ''):
                    red_envelopes_wechat(withdraw_record_obj)
                else:
                    pass
            elif origin == u'支付宝提现':
                if user_obj.get('alipay_account', ''):
                    start_transfer_alipay(withdraw_record_obj)
                else:
                    pass
            else:
                pass
    else:
        if origin == u'微信提现':
            if user_obj.get('wx_uid', ''):
                red_envelopes_wechat(withdraw_record_obj)
            else:
                pass
        elif origin == u'支付宝提现':
            if user_obj.get('alipay_account', ''):
                start_transfer_alipay(withdraw_record_obj)
            else:
                pass
    if withdraw_record.find_one({'user_id': user_id, 'status': 1}):
        withdraw_status = -1
    elif withdraw_record.find_one({'user_id': user_id, 'status': 0}):
        withdraw_status = 1
    elif withdraw_record.find_one({'user_id': user_id, 'status': -1}):
        withdraw_status = -2
    else:
        withdraw_status = 0
    user.update({'_id': ObjectId(user_id)}, {'$set': {'withdraw_status': withdraw_status}})


def start_transfer_alipay(withdraw_record_obj, review_name=u'系统自动'):
    """
    支付宝 单笔转账到支付宝账户接口
    :param withdraw_record_obj:
    :return:
    """
    user_id = withdraw_record_obj.get('user_id', '')
    user_obj = user.find_one({'_id': ObjectId(user_id)})
    alipay_account = user_obj.get('alipay_account', '')
    cash_value = withdraw_record_obj.get('value', '')
    amount = float('%.2f' % (float(cash_value) / float(100)))
    serial_number = withdraw_record_obj.get('serial_number', '')
    if conf_ver == 'conf.ProductionConfig':
        try:
            Payment_obj = Payment('2019101568374962', '')
            result_status, error_code = Payment_obj.pay(serial_number, alipay_account, amount,
                                                        user_obj.get('alipay_name', ''))
        except Exception as e:
            result_status, error_code = False, u'网络错误' + str(e)
    else:
        result_status, error_code = True, u'成功'
    if result_status:
        # 提现成功
        successful_notification(user_obj.get('wx_uid'), withdraw_record_obj, user_id, user_obj)
        if withdraw_record.find({'user_id': user_id, 'status': 1}).count() == 0:
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'status': 1, 'review_name': review_name, 'err_code': error_code,
                                                 'review_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}})
            invite_id = user_obj.get('invite_id', '')
            if invite_id:
                redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 2, 'invite_id': invite_id,
                                                                   'user_id': user_id}))
                redis_invite_code.lpush('invite_activity', json.dumps({'type': 1, 'invite_id': invite_id,
                                                                       'user_id': user_id}))
        else:
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'status': 1, 'review_name': review_name, 'err_code': error_code,
                                                 'review_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}})
    elif error_code == 'PAYEE_ACC_OCUPIED':
        try:
            Payment_obj = Payment('2019101568374962', '')
            result_status, error_code = Payment_obj.pay(serial_number, alipay_account, amount,
                                                        user_obj.get('alipay_name', ''))
        except Exception as e:
            result_status, error_code = False, u'网络错误' + str(e)
        if result_status:
            # 提现成功
            successful_notification(user_obj.get('wx_uid'), withdraw_record_obj, user_id, user_obj)
            if withdraw_record.find({'user_id': user_id, 'status': 1}).count() == 0:
                withdraw_record.update_one({'serial_number': serial_number},
                                           {'$set': {'status': 1, 'review_name': review_name, 'err_code': error_code,
                                                     'review_time': datetime.now().strftime(
                                                         format='%Y-%m-%d %H:%M:%S')}})
                invite_id = user_obj.get('invite_id', '')
                if invite_id:
                    redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 2, 'invite_id': invite_id,
                                                                       'user_id': user_id}))
                    redis_invite_code.lpush('invite_activity', json.dumps({'type': 1, 'invite_id': invite_id,
                                                                           'user_id': user_id}))
            else:
                withdraw_record.update_one({'serial_number': serial_number},
                                           {'$set': {'status': 1, 'review_name': review_name, 'err_code': error_code,
                                                     'review_time': datetime.now().strftime(
                                                         format='%Y-%m-%d %H:%M:%S')}})

    if not result_status:
        remark = ''
        if error_code in [u'支付宝提现系统升级中！', 'INVALID_PARAMETER', 'PAYCARD_UNABLE_PAYMENT',
                          'PAYER_DATA_INCOMPLETE', 'PERMIT_CHECK_PERM_LIMITED', 'PAYER_STATUS_ERROR',
                          'PAYER_STATUS_ERROR', 'PAYER_DATA_INCOMPLETE', 'PAYMENT_INFO_INCONSISTENCY',
                          'CERT_MISS_TRANS_LIMIT', 'CERT_MISS_ACC_LIMIT', 'PAYEE_ACC_OCUPIED',
                          'MEMO_REQUIRED_IN_TRANSFER_ERROR', 'PERMIT_PAYER_LOWEST_FORBIDDEN', 'PERMIT_PAYER_FORBIDDEN',
                          'PERMIT_CHECK_PERM_IDENTITY_THEFT', 'REMARK_HAS_SENSITIVE_WORD', 'ACCOUNT_NOT_EXIST',
                          'PAYER_CERT_EXPIRED', 'SYNC_SECURITY_CHECK_FAILED', 'TRANSFER_ERROR']:
            remark = u'支付宝提现系统升级中！请尝试微信提现'
        elif error_code in ['PERM_AML_NOT_REALNAME_REV', 'PERM_AML_NOT_REALNAME_REV', 'PERMIT_NON_BANK_LIMIT_PAYEE']:
            remark = u'请登录支付宝站内或手机客户端完善身份信息后，重试！'
        elif error_code in ['PAYEE_NOT_EXIST', 'PERMIT_NON_BANK_LIMIT_PAYEE']:
            remark = u'支付宝账号不存在！请检查之后重试'
        elif error_code == 'PAYEE_USER_INFO_ERROR':
            remark = u'支付宝账号和姓名不匹配，请确认姓名是否正确！'
        elif error_code in [u'服务暂时不可用！', 'SYSTEM_ERROR', 'PAYER_BALANCE_NOT_ENOUGH']:
            pass
        else:
            pass
        if remark:
            user.update_one({'_id': ObjectId(user_id)}, {'$inc': {'balance': cash_value}})
            withdraw_record_obj['remark'] = remark
            failure_notification(user_obj.get('wx_uid'), withdraw_record_obj, remark, user_obj)
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'status': -1, 'remark': remark,
                                                 'err_code': error_code, 'review_name': review_name,
                                                 'review_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}})
        else:
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'remark': remark, 'err_code': error_code}})


# def red_envelopes_wechat(withdraw_record_obj, review_name=u'系统自动'):
#     """
#     微信发红包
#     :param withdraw_record_obj:
#     :return:
#     """
#     user_id = withdraw_record_obj.get('user_id', '')
#     user_obj = user.find_one({'_id': ObjectId(user_id)})
#     openid = user_obj.get('wx_uid', '')
#     cash_value = withdraw_record_obj.get('value', '')
#     serial_number = withdraw_record_obj.get('serial_number', '')
#     try:
#         if conf_ver == 'conf.ProductionConfig':
#             client_ip = '47.103.141.42'
#         else:
#             client_ip = '47.101.67.173'
#
#         result_status, error_code = sendredpack(re_openid=openid, total_amount=cash_value, mch_billno=serial_number,
#                                                 client_ip=client_ip)
#     except Exception, e:
#         result_status, error_code = False, u'网络错误' + str(e)
#     if result_status:
#         # 提现成功
#         # successful_notification(user_obj.get('wx_uid'), withdraw_record_obj, user_id, user_obj)
#         if withdraw_record.find({'user_id': user_id, 'status': 1}).count() == 0:
#             withdraw_record.update_one({'serial_number': serial_number},
#                                        {'$set': {'status': 1, 'review_name': review_name, 'err_code': error_code,
#                                                  'review_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}})
#             invite_id = user_obj.get('invite_id', '')
#             if invite_id:
#                 redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 2, 'invite_id': invite_id,
#                                                                    'user_id': user_id}))
#                 redis_invite_code.lpush('invite_activity', json.dumps({'type': 1, 'invite_id': invite_id,
#                                                                        'user_id': user_id}))
#         else:
#             withdraw_record.update_one({'serial_number': serial_number},
#                                        {'$set': {'status': 1, 'review_name': review_name, 'err_code': error_code,
#                                                  'review_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}})
#     else:
#         remark = ''
#         if error_code == 'NO_AUTH':
#             remark = u'您的账号异常，已被微信拦截！请尝试支付宝提现'
#         elif error_code == 'SENDNUM_LIMIT':
#             remark = u'您今日微信提现次数已达上限！请尝试支付宝提现'
#         elif error_code == 'RCVDAMOUNT_LIMIT':
#             remark = u'您今日微信提现金额已达上限！请尝试支付宝提现'
#         elif error_code in ['ILLEGAL_APPID', 'FATAL_ERROR', 'CA_ERROR', 'SIGN_ERROR', 'XML_ERROR', 'API_METHOD_CLOSED',
#                             'NOTENOUGH', 'OPENID_ERROR', 'MSGAPPID_ERROR', 'ACCEPTMODE_ERROR', 'PARAM_ERROR',
#                             'SENDAMOUNT_LIMIT']:
#             remark = u'微信提现系统维护中！请尝试支付宝提现'
#         elif error_code == 'MONEY_LIMIT':
#             remark = u'微信提现不支持此金额！请尝试支付宝提现'
#         elif error_code == 'SEND_FAILED':
#             remark = u'微信提现系统升级！请再次重试'
#         elif error_code in ['SYSTEMERROR', 'PROCESSING']:
#             pass
#         elif error_code in ['FREQ_LIMIT']:
#             pass
#         else:
#             pass
#         if remark:
#             try:
#                 if conf_ver == 'conf.ProductionConfig':
#                     client_ip = '47.103.141.42'
#                 else:
#                     client_ip = '47.101.67.173'
#
#                 result_status, error_code = paymkttransfers(re_openid=openid, total_amount=cash_value,
#                                                             mch_billno=serial_number, client_ip=client_ip)
#             except Exception, e:
#                 result_status, error_code = False, u'网络错误' + str(e)
#             if result_status:
#                 # 提现成功
#                 successful_notification(user_obj.get('wx_uid'), withdraw_record_obj, user_id, user_obj)
#                 if withdraw_record.find({'user_id': user_id, 'status': 1}).count() == 0:
#                     withdraw_record.update_one({'serial_number': serial_number},
#                                                {'$set': {'status': 1, 'review_name': review_name,
#                                                          'err_code': error_code, 'is_transfer': 1,
#                                                          'review_time': datetime.now().strftime(
#                                                              format='%Y-%m-%d %H:%M:%S')}})
#                     invite_id = user_obj.get('invite_id', '')
#                     if invite_id:
#                         redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 2, 'invite_id': invite_id,
#                                                                            'user_id': user_id}))
#                         redis_invite_code.lpush('invite_activity', json.dumps({'type': 1, 'invite_id': invite_id,
#                                                                                'user_id': user_id}))
#                 else:
#                     withdraw_record.update_one({'serial_number': serial_number},
#                                                {'$set': {'status': 1, 'review_name': review_name,
#                                                          'err_code': error_code,
#                                                          'review_time': datetime.now().strftime(
#                                                              format='%Y-%m-%d %H:%M:%S')}})
#             else:
#                 remark = ''
#                 if error_code == 'NO_AUTH':
#                     remark = u'您的账号异常，已被微信拦截！请尝试支付宝提现'
#                 elif error_code == 'V2_ACCOUNT_SIMPLE_BAN':
#                     remark = u'您的提现微信号暂未实名暂时无法提现！请尝试支付宝提现'
#                 elif error_code == 'SENDNUM_LIMIT':
#                     remark = u'您今日微信提现金额已达上限！请尝试支付宝提现'
#                 elif error_code in ['AMOUNT_LIMIT', 'PARAM_ERROR', 'OPENID_ERROR', 'SEND_FAILED', 'NOTENOUGH',
#                                     'NAME_MISMATCH', 'SIGN_ERROR', 'XML_ERROR', 'FATAL_ERROR', 'FREQ_LIMIT',
#                                     'MONEY_LIMIT', 'CA_ERROR', 'PARAM_IS_NOT_UTF8', 'RECV_ACCOUNT_NOT_ALLOWED',
#                                     'PAY_CHANNEL_NOT_ALLOWED']:
#                     remark = u'微信提现系统维护中！请尝试支付宝提现'
#                 elif error_code in ['SYSTEMERROR', 'SEND_FAILED']:
#                     pass
#                 else:
#                     pass
#                 if remark:
#                     user.update_one({'_id': ObjectId(user_id)}, {'$inc': {'balance': cash_value}})
#                     withdraw_record_obj['remark'] = remark
#                     failure_notification(openid, withdraw_record_obj, remark, user_obj)
#                     withdraw_record.update_one({'serial_number': serial_number},
#                                                {'$set': {'status': -1, 'remark': remark,
#                                                          'err_code': error_code, 'review_name': review_name,
#                                                          'review_time': datetime.now().strftime(
#                                                              format='%Y-%m-%d %H:%M:%S')}})
#         else:
#             withdraw_record.update_one({'serial_number': serial_number},
#                                        {'$set': {'remark': remark, 'err_code': error_code}})


def red_envelopes_wechat(withdraw_record_obj, review_name=u'系统自动'):
    """
    微信企业 转账
    :param withdraw_record_obj:
    :return:
    """
    user_id = withdraw_record_obj.get('user_id', '')
    user_obj = user.find_one({'_id': ObjectId(user_id)})
    openid = user_obj.get('wx_uid', '')
    cash_value = withdraw_record_obj.get('value', '')
    serial_number = withdraw_record_obj.get('serial_number', '')
    if conf_ver == 'conf.ProductionConfig':
        try:
            if conf_ver == 'conf.ProductionConfig':
                client_ip = '47.103.141.42'
            else:
                client_ip = '47.101.67.173'

            result_status, error_code = paymkttransfers(re_openid=openid, total_amount=cash_value,
                                                        mch_billno=serial_number, client_ip=client_ip,
                                                        check_name='NO_CHECK', re_user_name='')
        except Exception as e:
            result_status, error_code = False, u'网络错误' + str(e)
    else:
        result_status, error_code = True, u'成功'
    if result_status:
        # 提现成功
        successful_notification(user_obj.get('wx_uid'), withdraw_record_obj, user_id, user_obj)
        if withdraw_record.find({'user_id': user_id, 'status': 1}).count() == 0:
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'status': 1, 'review_name': review_name,
                                                 'err_code': error_code, 'is_transfer': 1,
                                                 'review_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}})
            invite_id = user_obj.get('invite_id', '')
            if invite_id:
                redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 2, 'invite_id': invite_id,
                                                                   'user_id': user_id}))
                redis_invite_code.lpush('invite_activity', json.dumps({'type': 1, 'invite_id': invite_id,
                                                                       'user_id': user_id}))
        else:
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'status': 1, 'review_name': review_name, 'err_code': error_code,
                                                 'review_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')}})
    else:
        remark = ''
        if error_code == 'NO_AUTH':
            remark = u'您的账号异常，已被微信拦截！请尝试支付宝提现'
        elif error_code == 'V2_ACCOUNT_SIMPLE_BAN':
            remark = u'您的提现微信号暂未实名暂时无法提现！请实名之后再提现'
        elif error_code == 'SENDNUM_LIMIT':
            remark = u'您今日微信提现金额已达上限！请尝试支付宝提现'
        elif error_code in ['AMOUNT_LIMIT', 'PARAM_ERROR', 'OPENID_ERROR', 'SEND_FAILED', 'NOTENOUGH',
                            'NAME_MISMATCH', 'SIGN_ERROR', 'XML_ERROR', 'FATAL_ERROR', 'FREQ_LIMIT',
                            'MONEY_LIMIT', 'CA_ERROR', 'PARAM_IS_NOT_UTF8', 'RECV_ACCOUNT_NOT_ALLOWED',
                            'PAY_CHANNEL_NOT_ALLOWED']:
            remark = u'微信提现系统维护中！请尝试支付宝提现'
        elif error_code in ['SYSTEMERROR', 'SEND_FAILED']:
            pass
        else:
            pass
        if remark:
            user.update_one({'_id': ObjectId(user_id)}, {'$inc': {'balance': cash_value}})
            withdraw_record_obj['remark'] = remark
            failure_notification(openid, withdraw_record_obj, remark, user_obj)
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'status': -1, 'remark': remark,
                                                 'err_code': error_code, 'review_name': review_name,
                                                 'review_time': datetime.now().strftime(
                                                     format='%Y-%m-%d %H:%M:%S')}})
        else:
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'remark': remark, 'err_code': error_code}})


def red_envelopes_wechat_ccdj(withdraw_record_obj):
    """
    微信发红包
    :param withdraw_record_obj:
    :return:
    """
    user_id = withdraw_record_obj.get('user_id', '')
    user_obj = user.find_one({'_id': ObjectId(user_id)})
    openid = user_obj.get('wx_uid', '')
    cash_code = user_obj.get('ccdj_code', '')
    cash_value = withdraw_record_obj.get('value', '')
    serial_number = withdraw_record_obj.get('serial_number', '')
    time_stamp = int(time.time() * 1000)
    data = {'openid': openid, 'cash_code': cash_code, 'time_stamp': time_stamp, 'cash_value': cash_value,
            'serial_number': serial_number, 'type': 1}
    sign = get_sign_params(data).upper()
    data['sign'] = sign
    req = requests.post('https://www.xxdianjing.com/Api/OutCustom/cash', data=data)
    req_json = req.json()

    if req_json.get('code') == 0:
        stauts = req_json.get('status')
        err_code = req_json.get('err_code')
        remark = req_json.get('msg')
        if stauts == 1:
            # 提现成功
            successful_notification(user_obj.get('wx_uid'), withdraw_record_obj, user_id, user_obj)
            if withdraw_record.find({'user_id': user_id, 'status': 1}).count() == 0:
                invite_id = user_obj.get('invite_id', '')
                if invite_id:
                    redis_invite_code.lpush('invite_json', json.dumps({'is_bind': 2, 'invite_id': invite_id,
                                                                       'user_id': user_id}))
                    redis_invite_code.lpush('invite_activity', json.dumps({'type': 1, 'invite_id': invite_id,
                                                                           'user_id': user_id}))
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'red_envelopes_status': 1, 'status': 1}})
        elif stauts == -1:
            if req_json.get('err_code') not in ['SYSTEMERROR', 'PROCESSING']:

                withdraw_record_obj['remark'] = remark
                user.update_one({'_id': ObjectId(user_id)}, {'$inc': {'balance': cash_value}})
                failure_notification(openid, withdraw_record_obj, data, user_obj)
                withdraw_record.update_one({'serial_number': serial_number},
                                           {'$set': {'red_envelopes_status': 1, 'status': -1, 'remark': remark,
                                                     'err_code': err_code}})
            else:
                withdraw_record.update_one({'serial_number': serial_number},
                                           {'$set': {'red_envelopes_status': 1, 'remark': remark,
                                                     'err_code': err_code}})
        else:
            withdraw_record.update_one({'serial_number': serial_number},
                                       {'$set': {'red_envelopes_status': 1, 'remark': remark,
                                                 'err_code': err_code}})
    withdraw_record.update_one({'serial_number': serial_number}, {'$set': {'req_json': req_json}})


def generate_station_notice(user_id, title, des, type_num, value, content, subsidy_des, is_bulletin):
    """
    :param user_id: 用户ID
    :param title: 消息标题
    :param des: 消息描述
    :param type_num: 补贴类型 0为没有补贴 1为补贴热量  2为补贴现金
    :param value: 补贴值
    :param content: 通知内容
    :param subsidy_des: u'补贴说明'
    :param is_bulletin: u'是否弹框  0为不弹框  1为弹框'
    :return:
    """
    station_notice.insert_one({'user_id': user_id, 'title': title, 'des': des, 'type_num': type_num, 'value': value,
                               'content': content, 'status': 0, 'is_bulletin': is_bulletin, 'subsidy_des': subsidy_des,
                               'created_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})


def get_current_real_name():
    return session['real_name']


def get_current_username():
    return session['username']


def get_user_by_id(user_id):
    user_obj = user.find_one({'_id': user_id})
    return user_obj


def get_datetime_str(format_str='%Y-%m-%d %H:%M:%S', time=None):
    if time is None:
        time = datetime.now()
    return time.strftime(format_str)


if __name__ == '__main__':
    user_cur = user.find()
    for user_obj in user_cur:
        user_id = str(user_obj.get('_id'))
        generate_station_notice(user_id, u'系统重大升级补热量2', u'系统重大升级补热量2', 1, 100, u'系统重大升级补热量2', u'系统升级2', 0)
