# -*- coding: utf8 -*-
# import sys
import logging 
# import os.path
# import time


from flask import Blueprint

from libs.common import get_request_params
from libs.crypt import XKcrypt
from libs.flask_ex import format_request_params, get_request_page_params, Resp, int_keys_processor, request_args_verify, \
    resource_processor, list_processor
from libs.permission import permissions_check
from model import (get_list_obj, create_obj, model, get_detail_obj, update_obj, delete_obj)
from libs.common import get_datetime_str

crypt_obj = XKcrypt()

# reload(sys)
# sys.setdefaultencoding('utf-8')

product_api_blue = Blueprint('product_api', __name__, url_prefix='/api/product')
logger = logging.getLogger()
logger.setLevel(logging.INFO)  
log_path = 'log/'

log_name = log_path + 'info.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')

fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

fh.setFormatter(formatter)
logger.addHandler(fh)

@product_api_blue.route('/my_list', methods=['get'])
@permissions_check('product:get', False)
def my_list():
    criteria = format_request_params(get_request_params(),
                                     model.default_values,
                                     int_keys_processor(model.int_keys))
    page_num, limit = get_request_page_params()
    page_obj = get_list_obj(criteria, page_num, limit)
    return Resp.ok(page_obj)


@product_api_blue.route('/add', methods=['POST'])
@permissions_check('product:add', False)
def add():
    data = format_request_params(get_request_params(),
                                 model.default_values,
                                 int_keys_processor(model.int_keys),
                                 # resource_processor=resource_processor(['thumbnail', 'image'], require=True),
                                 begin_processors=list_processor('image_list'),
                                 full_fields=True)
    create_obj(data)
    return Resp.ok()


@product_api_blue.route('/detail', methods=['get'])
@permissions_check('product:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def detail(_id):
    detail_obj = get_detail_obj(_id)
    return Resp.ok(detail_obj)

@product_api_blue.route('/copyproduct', methods=['post'])
@permissions_check('product:get', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def copyitem(_id):
    detail_obj = get_detail_obj(_id)
    del detail_obj[u'_id']
    del detail_obj[u'created_time']
    detail_obj[u'created_time']=get_datetime_str()
    logger.info(detail_obj)
    ret= create_obj(detail_obj)
    return Resp.ok()

@product_api_blue.route('/update', methods=['post'])
@permissions_check('product:edit', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def update(_id):
    update_dict = format_request_params(get_request_params(),
                                        model.default_values,
                                        int_keys_processor(model.int_keys),
                                        # resource_processor=resource_processor(['thumbnail', 'image'], require=False),
                                        begin_processors=list_processor('image_list'),
                                        )
    update_obj(_id, update_dict)
    return Resp.ok()


@product_api_blue.route('/delete', methods=['delete', 'post'])
@permissions_check('product:delete', False)
@request_args_verify('<ObjectId:_id>', ObjectIds=['_id'])
def delete(_id):
    delete_obj(_id)
    return Resp.ok()
