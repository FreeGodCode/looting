# -*- coding: utf8 -*-
# author: tefsky
import json

from libs.flask_ex import Resp


class ProcessError(Exception, Resp):
    def __init__(self, code, msg, status=200):
        data = {
            'code': code,
            'msg': msg
        }
        Resp.__init__(self, data, status)
