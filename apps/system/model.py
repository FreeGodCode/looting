# -*- coding: utf8 -*-
import copy

from pymongo.errors import DuplicateKeyError

from libs.db import system

default_des = {
    'planet_name': u'默认星球名字',
    'img_url': u'默认星球头像',
    'ball_avatar': u'球主头像',
    'planet_red_total': u'默认星球总共抢的红包值',
    'planet_commission_total': u'默认星球总的分润',
    'qn_url': u'七牛空间url',
    'bucket_name': u'七牛空间名字',
    'access_key': u'七牛空间apiKey',
    'secret_key': u'七牛空间apiSecret',
    'gzh_qrcode': u'公众号二维码',
    'gzh_name': u'公众号名字',
    'gzh_token': u'公众号令牌(Token)',
    'gzh_appid': u'公众号开发者ID(AppID)',
    'gzh_appsecret': u'公众号秘钥(AppSecret)',
    'android_dowload_url': u'安卓版本最新下载',
    'ios_dowload_url': u'苹果版本最新下载',
    'heat_art_id': u'热量页面醒目文章ID',
    'income_art_id': u'收益页面醒目文章ID',
    'withdraw_art_id': u'提现页面醒目文章ID',

}

default_values = {
    'planet_name': u'',
    'img_url': u'',
    'ball_avatar': u'',
    'planet_red': 0,
    'qn_url': u'',
    'bucket_name': u'',
    'access_key': u'',
    'secret_key': u'',
    'gzh_qrcode': u'',
    'gzh_name': u'',
    'gzh_token': u'',
    'gzh_appid': u'',
    'gzh_appsecret': u'',
    'android_dowload_url': u'',
    'ios_dowload_url': u'',
    'heat_art_id': u'',
    'income_art_id': u'',
    'withdraw_art_id': u'',
}

int_key = ['planet_red_total', 'planet_commission_total']

float_key = []


def _insert(data):
    global default_values
    add_dict = copy.copy(default_values)
    for key in default_values:
        if key in data:
            _values = data.get(key)
            # if isinstance(_values, str) or isinstance(_values, unicode):
            if isinstance(_values, str):
                _values = _values.strip()
            if key in int_key:
                try:
                    _values = int(_values)
                except:
                    return {'status': False, 'msg': u'参数错误'}
            if key in float_key:
                try:
                    _values = float(_values)
                except:
                    return {'status': False, 'msg': u'参数错误'}
            add_dict.update({key: _values})
    try:
        system.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True}


if __name__ == '__main__':
    _insert({})
