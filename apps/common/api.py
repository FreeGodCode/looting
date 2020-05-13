# -*- coding: utf8 -*-
import sys
import uuid

from flask import Blueprint, request

from libs.crypt import XKcrypt
from libs.flask_ex import Resp, request_args_verify
from libs.permission import permissions_check

crypt_obj = XKcrypt()

reload(sys)
sys.setdefaultencoding('utf-8')

common_api_blue = Blueprint('common_api', __name__, url_prefix='/api/common')


@common_api_blue.route('/upload', methods=['post'])
@permissions_check('common:upload', False)
@request_args_verify('file_url', Resources=['file'], ResourceRequire=True)
def upload(file_url):
    pass
    return Resp.ok(file_url)
