# -*- coding: utf8 -*-
# import sys

from flask import Blueprint, jsonify, request

# from libs.common import login_api_check, judging_permissions
from libs.db import system
from libs.permission import permissions_check
from libs.utils import upload_img
from model import (default_values, int_key, float_key, _insert)

# reload(sys)
# sys.setdefaultencoding("utf-8")

system_api_blue = Blueprint('system_api', __name__, url_prefix='/api/system')


@system_api_blue.route('/detail', methods=['get'])
@permissions_check('system:get')
def detail():
    _obj = system.find_one({})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'暂不存在'})
    _obj['_id'] = str(_obj['_id'])
    return jsonify({'code': 200, 'data': _obj})


@system_api_blue.route('/update', methods=['post'])
@permissions_check('system:get', False)
def update():
    _update = {}
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    _obj = system.find_one()
    if not _obj:
        result = _insert(data)
        if result.get('status'):
            return jsonify({'code': 200, 'msg': u'成功'})
        return jsonify({'code': 200, 'msg': u'不存在'})

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
                    return jsonify({'code': 201, 'msg': u'参数错误'})
            if key in float_key:
                try:
                    _values = float(_values)
                except:
                    return jsonify({'code': 201, 'msg': u'参数错误'})
            if _obj.get(key) != _values:
                _update.update({key: _values})
    if 'img_url' in _update:
        del _update['img_url']
    _file = request.files
    img_url_file = _file.get('img_url')
    if img_url_file:
        result, img_url = upload_img(img_url_file)
        if not result:
            return jsonify({'code': 206, 'msg': img_url})
        _update.update({'img_url': img_url})

    if 'ball_avatar' in _update:
        del _update['ball_avatar']
    _file = request.files
    ball_avatar_file = _file.get('ball_avatar')
    if ball_avatar_file:
        result, img_url = upload_img(ball_avatar_file)
        if not result:
            return jsonify({'code': 206, 'msg': img_url})
        _update.update({'ball_avatar': img_url})
    if 'gzh_qrcode' in _update:
        del _update['gzh_qrcode']
    _file = request.files
    gzh_qrcode_file = _file.get('gzh_qrcode')
    if gzh_qrcode_file:
        result, img_url = upload_img(gzh_qrcode_file)
        if not result:
            return jsonify({'code': 206, 'msg': img_url})
        _update.update({'gzh_qrcode': img_url})

    if _update:
        try:
            system.update_one({'_id': _obj.get('_id')}, {'$set': _update})
            return jsonify({'code': 200, 'msg': u'成功'})
        except:
            pass
    else:
        return jsonify({'code': 203, 'msg': u'无更新数据'})
    return jsonify({'code': 204, 'msg': u'失败'})
