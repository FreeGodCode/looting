# -*- coding: utf8 -*-
# author: tefsky

import json
from datetime import datetime

from bson import ObjectId




__null_func = lambda x: x


def get_pageable(_cur, page_num, limit, processor=__null_func):
    _count = _cur.count()
    num = _count / limit + ((_count % limit) > 0 and 1 or 0)
    _list = get_listable(_cur, page_num, limit, processor)
    return {'num': num, 'count': _count, 'page': page_num, 'list': _list}


def get_listable(_cur, page_num, limit, processor=__null_func):
    page_num = page_num - 1
    _count = _cur.count()
    _list = list()
    if _count > (page_num * limit):
        cur_list = _cur.skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            if _obj.has_key('_id'):
                _obj['_id'] = str(_obj['_id'])
            proced_obj = processor(_obj)
            _list.append(proced_obj)
    return _list
