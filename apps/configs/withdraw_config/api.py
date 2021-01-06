# -*- coding: utf8 -*-
# import sys

from flask import Blueprint

from apps.configs.withdraw_config.model import model, option_model, class_model
from libs.common import get_request_params
from libs.flask_ex import get_request_page_params, format_request_params, request_args_verify, int_keys_processor, Resp, \
    float_keys_processor, exists_processor
from libs.permission import permissions_check

# reload(sys)
# sys.setdefaultencoding('utf-8')

withdraw_config_api_blue = Blueprint('withdraw_config_api', __name__, url_prefix='/api/withdraw_config')


@withdraw_config_api_blue.route('/my_list', methods=['get'])
@permissions_check('withdraw_config:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values)
    page_num, limit = get_request_page_params()
    page_obj = model.get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@withdraw_config_api_blue.route('/detail', methods=['get'])
@permissions_check('withdraw_config:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = model.get_detail_obj(_id)
    return Resp.ok(detail_obj)


@withdraw_config_api_blue.route('/add', methods=['POST'])
@permissions_check('withdraw_config:add', False)
def add():
    data = get_request_params()
    withdraw_data = format_request_params(data,
                                          model.default_values,
                                          [
                                              int_keys_processor(model.int_keys)
                                          ],
                                          convert_object_id=True,
                                          full_fields=True)
    model.create_obj(withdraw_data)
    return Resp.ok()


@withdraw_config_api_blue.route('/update', methods=['post'])
@permissions_check('withdraw_config:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_data = format_request_params(get_request_params(),
                                        model.default_values,
                                        [
                                            int_keys_processor(model.int_keys)
                                        ],
                                        convert_object_id=True)
    model.update_obj(_id, update_data)
    return Resp.ok()


@withdraw_config_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('withdraw_config:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    model.remove(_id)
    return Resp.ok()


@withdraw_config_api_blue.route('/option_update', methods=['put'])
@permissions_check('withdraw_config:edit', False)
def option_update():
    update_data = format_request_params(get_request_params(),
                                        option_model.default_values,
                                        [
                                            int_keys_processor(option_model.int_keys),
                                            float_keys_processor(option_model.float_keys)
                                        ],
                                        begin_processors=exists_processor(option_model.switch_keys),
                                        convert_object_id=True,
                                        full_fields=True)
    option_model.update_obj(update_data)
    return Resp.ok()


@withdraw_config_api_blue.route('/option_detail', methods=['get'])
@permissions_check('withdraw_config:get', False)
def option_detail():
    base_detail_obj = option_model.get_detail_obj()
    return Resp.ok(base_detail_obj)


@withdraw_config_api_blue.route('/class_list', methods=['get'])
@permissions_check('withdraw_config:get')
def class_list():
    criteria = format_request_params(get_request_params(),
                                     class_model.default_values,
                                     int_keys_processor(class_model.int_keys))
    page_num, limit = get_request_page_params()
    page_obj = class_model.get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@withdraw_config_api_blue.route('/class_add', methods=['post'])
@permissions_check('withdraw_config:add')
def add_class():
    data = format_request_params(get_request_params(),
                                 class_model.default_values,
                                 int_keys_processor(class_model.int_keys),
                                 full_fields=True)
    class_model.create_obj(data)
    return Resp.ok()


@withdraw_config_api_blue.route('/class_update', methods=['put'])
@permissions_check('withdraw_config:edit')
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def update_class(_id):
    data = format_request_params(get_request_params(),
                                 class_model.default_values,
                                 int_keys_processor(class_model.int_keys))
    class_model.update_obj(_id, data)
    return Resp.ok()


@withdraw_config_api_blue.route('/class_detail', methods=['get'])
@permissions_check('withdraw_config:get')
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def get_class_detail(_id):
    detail_obj = class_model.get_detail_obj(_id)
    return Resp.ok(detail_obj)


@withdraw_config_api_blue.route('/class_delete', methods=['delete'])
@permissions_check('withdraw_config:delete')
@request_args_verify("<ObjectId:_id>", ObjectIds=['_id'])
def remove_class(_id):
    class_model.remove_obj(_id)
    return Resp.ok()
