# -*- coding: utf8 -*-
from bson import ObjectId
from flask import Blueprint, render_template, request

from libs.common import login_check
from libs.db import feedback, station_notice

feedback_blue = Blueprint('feedback', __name__, template_folder='../../templates',
                          static_folder='../../statices',
                          url_prefix='/feedback')


@feedback_blue.route('/list', methods=['get'])
@login_check
def _list():
    return render_template('feedback/list.html')


@feedback_blue.route('/edit', methods=['get'])
@login_check
def edit():
    _id = request.args.get('_id', '')
    if not _id:
        return '404'
    _obj = feedback.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return '404'
    _obj['_id'] = _id
    content = _obj.get('content')
    image_list = _obj.get('image_list')
    for inage_url in image_list:
        content += '<p><img src="' + inage_url + '"></p>'
    station_notice_content = ''
    station_notice_obj = station_notice.find_one({'feedback_id': _obj.get('_id')})
    if station_notice_obj:
        station_notice_content = station_notice_obj.get('content', '')
    return render_template('feedback/edit.html', _id=_id, content=content,
                           station_notice_content=station_notice_content)
