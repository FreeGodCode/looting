# -*- coding: utf8 -*-
import sys

from flask import Blueprint, request, jsonify

from libs.common import login_api_check, judging_permissions
from libs.db import leaderboard
from model import (default_values, int_key)

reload(sys)
sys.setdefaultencoding("utf-8")

leaderboard_api_blue = Blueprint('leaderboard_api', __name__, url_prefix='/api/leaderboard')


@leaderboard_api_blue.route('/my_list', methods=['get'])
@login_api_check()
def my_list():
    access_status = judging_permissions('1_3_3')
    if access_status.get('code') != 200:
        return jsonify(access_status)
    criteria = {}
    # 支持表格字段里的任何搜索
    for item in default_values:
        req_value = request.args.get(item)
        if req_value:
            req_value = req_value.strip()
            if item in int_key:
                try:
                    req_value = int(req_value)
                except:
                    return jsonify({'code': 201, 'msg': u'参数错误'})
                criteria.update({item: req_value})
            else:
                criteria.update({item: {'$regex': req_value}})
    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = leaderboard.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('number_people_invited', -1), ('reg_time', 1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                number_people_invited = _obj.get('number_people_invited')
                total_invitation_num = _obj.get('total_invitation_num', 0)
                _obj['fission_num'] = total_invitation_num - number_people_invited
                _list.append(_obj)
            except Exception, e:
                print e
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})
