# -*- coding: utf8 -*-
# author: tefsky

import functools
import re
from datetime import datetime

from bson import ObjectId
from flask import Flask, Response, json, request
from flask import jsonify
from flask.ctx import RequestContext
from werkzeug.routing import BaseConverter

from libs.common import get_request_params
from libs.funcutils import get_func_arg_names
from libs.utils import upload_img


class RegexConverter(BaseConverter):
    """
    正则转换器 - 让路由支持正则
    """

    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


class MyRequestContext(RequestContext):
    """
    RequestConext 请求上下文对象
    """

    def __init__(self, *args, **kwargs):
        RequestContext.__init__(self, *args, **kwargs)

    def match_request(self):
        """
        请求匹配,默认更具App注册的url规则进行匹配
        :return:
        """
        return RequestContext.match_request(self)


class JsonEncoder(json.JSONEncoder):
    """
    序列化支持 ObjectId 与 datetime
    """

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, o)


class FlaskEx(Flask):
    """
    Flask 扩展类
    """
    json_encoder = JsonEncoder

    def __init__(self, *args, **kwargs):
        Flask.__init__(self, *args, **kwargs)
        # 让flask 路由支持正则匹配
        self.url_map.converters['regex'] = RegexConverter

    def request_context(self, environ):
        return MyRequestContext(self, environ)


class FlaskProcessError(Exception):
    def __init__(self, code, msg, ext=None):
        self.code = code
        self.msg = msg
        self.ext = ext

    def get_code(self):
        return self.code

    def get_msg(self):
        return self.msg

    def get_ext(self):
        return self.ext


class InternalProcessError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def get_code(self):
        return self.code

    def get_msg(self):
        return self.msg


convert_dict = {
    'string': lambda x: x is not None and str(x) or '',
    'str': lambda x: x is not None and str(x) or '',
    'int': lambda x: x is not None and int(x) or None,
    'unicode': lambda x: x is not None and unicode(x) or u'',
    'float': lambda x: x is not None and float(x) or None,
    'number': lambda x: x is not None and float(x) or None,
    'bool': lambda x: x is not None and bool(x) or None,
    'ObjectId': lambda x: x is not None and ObjectId(x) or None
}


def analytic_params(args):
    rule = r'<(.+?)\:([^ \:]+)(?:\:([0-9]+))?>'
    result_list = list()
    for arg_obj in args:
        if not isinstance(arg_obj, (str, unicode)):
            raise Exception('装饰器参数错误')
        match_obj = re.match(rule, arg_obj)
        if not match_obj:
            result_list.append(('string', arg_obj, None, True))
            continue
        else:
            result = list(match_obj.groups())
            type_name = result[0]
            if type_name.endswith('?'):
                result[0] = type_name[0:-1]
                result.append(False)
            else:
                result.append(True)
            result_list.append(result)
    return result_list


def generate_kwargs(func_obj, kwargs, analytic_list, request_params):
    param_names = get_func_arg_names(func_obj)
    for type_name, name, length, is_require in analytic_list:
        orig_val = request_params.get(name, None)
        try:
            val = convert_dict[type_name](orig_val)
        except (ValueError, TypeError) as e:
            raise FlaskProcessError(10003, u'%s : %s 不是一个有效的值' % (name, orig_val), (name, orig_val))
        if length and len(orig_val) != int(length):
            raise FlaskProcessError(10003, u'%s : %s 不是一个有效的值' % (name, orig_val), (name, orig_val))
        kwargs.update({name: val})
    return kwargs


def get_request_page_params(allow_null=True, params=None):
    """
    提取请求中的 limit,page_num 分页参数
    :return:
    """
    data = params
    if data is None:
        data = get_request_params()
    if allow_null:
        limit = int(data.get('limit', 10))
        page_num = int(data.get('page_num', 1))
    else:
        limit = int(data['limit'])
        page_num = int(data['page_num'])
    return page_num, limit


_null_func = lambda x, y: y
_null_func2 = lambda x, y: (False, y)
mg_regex_processor = lambda x, y: {'$regex': y}
null_field = []


def generic_fields_process(fields, generic_processor):
    def process(item, value):
        if item in fields:
            return True, generic_processor(value)
        else:
            return False, value

    return process


def generic_convert(processor):
    def _process(value):
        if isinstance(value, list):
            return map(lambda x: processor(x), value)
        elif isinstance(value, dict):
            for key in value.keys():
                value[key] = processor(value[key])
            return value
        else:
            return processor(value)

    return _process


def int_keys_processor(fields):
    return generic_fields_process(fields, generic_convert(lambda x: int(x)))


def float_keys_processor(fields):
    return generic_fields_process(fields, generic_convert(lambda x: float(x)))


def boolean_keys_processor(fields):
    return generic_fields_process(fields, generic_convert(lambda x: bool(x)))


def datetime_keys_processor(fields, pattern='%Y-%m-%d %H:%M:%S'):
    return generic_fields_process(fields, generic_convert(lambda x: datetime.strptime(x, pattern)))


def map_processor(pattern):
    def _process(dict_data):
        for key in dict_data.keys():
            result = re.match(pattern, key)
            if result:
                val = dict_data[key]
                del dict_data[key]
                new_key = result.group(1)
                new_sub_key = result.group(2)
                if dict_data.has_key(new_key):
                    dict_data[new_key][new_sub_key] = val
                else:
                    dict_data[new_key] = {new_sub_key: val}
        return dict_data

    return _process


def list_processor(key_name_list):
    if not isinstance(key_name_list, list):
        key_name_list = [key_name_list]

    def _process(dict_data):
        for key in dict_data.keys():
            names = filter(lambda x: key.startswith(x), key_name_list)
            if names:
                key_name = names[0]
                if dict_data.has_key(key_name):
                    dict_data[key_name].append(dict_data[key])
                else:
                    dict_data[key_name] = [dict_data[key]]
        return dict_data

    return _process


def exists_processor(key_name_list, default_values=(True, False)):
    if not isinstance(key_name_list, list):
        key_name_list = [key_name_list]

    def process(data):
        for key in key_name_list:
            if key in data.keys():
                data[key] = default_values[0]
            else:
                data[key] = default_values[1]
        return data

    return process


def resource_processor(res_names, suffix='_url', require=False):
    def _process():
        res_dict = dict()
        processed_list = list()
        for res_file in request.files:
            if res_file in res_names:
                result, url = upload_img(request.files.get(res_file))
                if not result:
                    raise FlaskProcessError(10003, u'资源上传失败: %s' % res_file)
                res_dict.update({res_file + suffix: url})
                processed_list.append(res_file)
        if require:
            result = filter(lambda x: x not in processed_list, res_names)
            if result:
                raise FlaskProcessError(10003, '', result)
        return res_dict

    return _process


# -----------------------------------------------------------------------------

def request_args_verify(*verify_args, **verify_kwargs):
    """
    请求参数检验,必须放在最内层
    :param args:
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = get_request_params()

                if verify_kwargs.has_key('Resources'):
                    res_suffix = '_url'
                    if verify_kwargs.has_key('ResourceSuffix'):
                        res_suffix = verify_kwargs['ResourceSuffix']
                    res_require = True
                    if verify_kwargs.has_key('ResourceRequire'):
                        res_require = verify_kwargs['ResourceRequire']
                    res_list = verify_kwargs.get('Resources')
                    try:
                        result = resource_processor(res_list, res_suffix, res_require)()
                        if result:
                            data.update(result)
                    except FlaskProcessError as e:
                        if e.get_ext():
                            return Resp.miss_require_params(e.get_ext())
                        return Resp.fail(e.get_msg())

                analytic_result = analytic_params(verify_args)
                result = filter(lambda x: x not in data.keys(),
                                map(lambda x: x[1],
                                    filter(lambda x: x[3], analytic_result)))
                if result:
                    return Resp.miss_require_params(result)

                if verify_kwargs.has_key('ObjectIds'):
                    key_list = verify_kwargs.get('ObjectIds')
                    for key in key_list:
                        _id = data.get(key, None)
                        if _id and not ObjectId.is_valid(_id):
                            return Resp.invalid_params([key])

                try:
                    kwargs = generate_kwargs(func, kwargs, analytic_result, data)
                except FlaskProcessError as e:
                    name, val = e.get_ext()
                    return Resp.invalid_params([name])
                result = func(*args, **kwargs)
                return result
            except FlaskProcessError as e:
                return jsonify({'code': e.get_code(), 'msg': e.get_msg()})

        return wrapper

    return decorator


def format_request_params(request_params, default_values, fields_processors=_null_func2, default_processor=_null_func,
                          convert_object_id=False, begin_processors=None, after_processor=None,
                          resource_processor=None, full_fields=False):
    data = request_params
    if begin_processors:
        if isinstance(begin_processors, list):
            for process_obj in begin_processors:
                data = process_obj(data)
        else:
            data = begin_processors(data)

    if resource_processor:
        try:
            res_dict = resource_processor()
            if res_dict:
                data.update(res_dict)
        except FlaskProcessError as e:
            if e.get_ext():
                msg = u'依赖资源: [%s]' % (','.join(e.get_ext()))
                raise InternalProcessError(10003, msg)
            raise InternalProcessError(10005, u'资源上传失败')

    new_data = dict()
    for item in default_values:
        req_value = data.get(item)
        if req_value not in [None, '']:
            if isinstance(req_value, (str, unicode)):
                req_value = req_value.strip()
            if convert_object_id and isinstance(req_value, (str, unicode)) and len(
                    req_value) == 24 and ObjectId.is_valid(req_value):
                req_value = ObjectId(req_value)
            if isinstance(fields_processors, list):
                result = False
                for func_process in fields_processors:
                    result, req_value = func_process(item, req_value)
                    if result:
                        break
            else:
                result, req_value = fields_processors(item, req_value)
            if not result:
                req_value = default_processor(item, req_value)
            new_data.update({item: req_value})

    if after_processor:
        new_data = after_processor(new_data)

    if full_fields:
        full_data = default_values
        full_data.update(new_data)
        new_data = full_data

    return new_data


class Resp(Response):
    _resp_dict = {
        'ok': ({'code': '200', 'msg': 'success'}, 200),
        'operation_fail': ({'code': 205, 'msg': u'操作失败'}, 200),
        'miss_require_params': ({'code': 201, 'msg': u'缺失依赖参数'}, 200),
        'invalid_params': ({'code': 201, 'msg': u'参数无效'}, 200),
    }

    def __init__(self, data, status, *args, **kwargs):
        indent = None
        separators = (',', ':')
        response_content = json.dumps(data, indent=indent, separators=separators)
        super(Resp, self).__init__(response_content, status, *args, **kwargs)

    @staticmethod
    def ok(data=None):
        resp_dict, status = Resp._resp_dict['ok']
        if data:
            resp_dict['data'] = data
        return Resp(resp_dict, status)

    @staticmethod
    def fail(msg=None):
        resp_dict, status = Resp._resp_dict['operation_fail']
        if msg:
            resp_dict['msg'] = msg
        return Resp(resp_dict, status)

    @staticmethod
    def miss_require_params(param_names=None):
        resp_dict, status = Resp._resp_dict['miss_require_params']
        if param_names is not None:
            resp_dict['msg'] = u'缺失依赖参数: [%s]' % (','.join(param_names))
        return Resp(resp_dict, status)

    @staticmethod
    def invalid_params(param_names=None, values=None):
        resp_dict, status = Resp._resp_dict['invalid_params']
        if param_names is not None:
            if values is not None:
                key_values = zip(param_names, values)
                content_list = list()
                for key_value in key_values:
                    content_list.append('{0}:{1}'.format(key_value[0], key_value[1]))
                resp_dict['msg'] = u'参数无效: [%s]' % (','.join(content_list))
            else:
                resp_dict['msg'] = u'参数无效: [%s]' % (','.join(param_names))
        return Resp(resp_dict, status)
