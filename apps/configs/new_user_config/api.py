# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from libs.common import get_request_params
from libs.flask_ex import format_request_params, int_keys_processor, Resp, float_keys_processor, exists_processor
from libs.permission import permissions_check
from .model import model

reload(sys)
sys.setdefaultencoding('utf-8')

new_user_config_api_blue = Blueprint('new_user_config_api', __name__, url_prefix='/api/new_user_config')


@new_user_config_api_blue.route('/detail', methods=['get'])
@permissions_check('new_user_config:get', False)
def detail():
    detail_obj = model.get_detail_obj()
    return Resp.ok(detail_obj)


@new_user_config_api_blue.route('/update', methods=['post'])
@permissions_check('new_user_config:edit', False)
def update():
    update_data = format_request_params(get_request_params(),
                                        model.default_values,
                                        [
                                            int_keys_processor(model.int_keys),
                                            float_keys_processor(model.float_keys)
                                        ],
                                        begin_processors=exists_processor('status'),
                                        convert_object_id=True,
                                        full_fields=True)
    model.update_obj(update_data)
    return Resp.ok()
