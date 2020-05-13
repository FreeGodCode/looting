# -*- coding: utf8 -*-
import sys

from flask import Blueprint

from apps.configs.invite_task_config.model import model
from libs.common import get_request_params
from libs.flask_ex import format_request_params, float_keys_processor, Resp, int_keys_processor, exists_processor
from libs.permission import permissions_check

reload(sys)
sys.setdefaultencoding('utf-8')

invite_task_config_api_blue = Blueprint('invite_task_config_api', __name__, url_prefix='/api/invite_task_config')


@invite_task_config_api_blue.route('/detail', methods=['get'])
@permissions_check('route_config:get', False)
def detail():
    # 支持表格字段里的任何搜索
    detail_obj = model.get_detail_obj()
    return Resp.ok(detail_obj)


@invite_task_config_api_blue.route('/update', methods=['post'])
@permissions_check('route_config:edit', False)
def update():
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        [
                                            int_keys_processor(model.int_keys),
                                            float_keys_processor(model.float_keys)
                                        ],
                                        begin_processors=exists_processor('status')
                                        )
    model.update_obj(update_dict)
    return Resp.ok()
