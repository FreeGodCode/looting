# -*- coding: utf8 -*-

from flask import Blueprint

from apps.domain_h5.model import model, get_list_obj, create_obj, get_detail_obj, update_obj, delete_obj
from libs.common import get_request_params
from libs.flask_ex import request_args_verify, Resp, format_request_params, int_keys_processor, get_request_page_params
from libs.permission import permissions_check

domain_h5_api_blue = Blueprint('domain_h5_api', __name__, url_prefix='/api/domain_h5')


@domain_h5_api_blue.route('/my_list', methods=['GET'])
@permissions_check('domain_h5:get', False)
def _list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys))
    page_num, limit = get_request_page_params()
    page_obj = get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@domain_h5_api_blue.route('/add', methods=['POST'])
@permissions_check('domain_h5:add', False)
def add():
    data = format_request_params(get_request_params(),
                                 model.default_values,
                                 int_keys_processor(model.int_keys),
                                 full_fields=True)
    create_obj(data)
    return Resp.ok()


@domain_h5_api_blue.route('/detail', methods=['GET'])
@permissions_check('domain_h5:get', False)
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_detail_obj(_id)
    return Resp.ok(detail_obj)


@domain_h5_api_blue.route('/update', methods=['POST'])
@permissions_check('domain_h5:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys))
    update_obj(_id, update_dict)
    return Resp.ok()


@domain_h5_api_blue.route('/delete', methods=['DELETE'])
@permissions_check('domain_h5:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    delete_obj(_id)
    return Resp.ok()
