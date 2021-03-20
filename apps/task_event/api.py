# -*- coding: utf8 -*-
# import sys

from flask import Blueprint

from apps.task_event.model import get_list_obj, model
from libs.common import get_request_params
from libs.crypt import XKcrypt
from libs.flask_ex import Resp, format_request_params, mg_regex_processor, int_keys_processor, \
    get_request_page_params
from libs.permission import permissions_check

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

task_event_api_blue = Blueprint('task_event_api', __name__, url_prefix='/api/task_event')


@task_event_api_blue.route('/my_list', methods=['get'])
@permissions_check('daily_task:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     [
                                         int_keys_processor(model.int_keys)
                                     ],
                                     mg_regex_processor)
    page_num, limit = get_request_page_params()
    page_obj = get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@task_event_api_blue.route('/repeatable_list', methods=['get'])
@permissions_check('daily_task:get', False)
def repeatable_list():
    page_num, limit = get_request_page_params()
    page_obj = get_list_obj({'repeatable': 1}, page_num, limit)
    return Resp.ok(page_obj)
