# -*- coding: utf8 -*-
import StringIO
import copy
import json
import string
import time

from bson import ObjectId
from flask import Blueprint, render_template, request, session, jsonify, make_response
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from libs.common import login_check, get_ip_area
from libs.crypt import XKcrypt
from libs.db import admin_user, login_log, redis_admin, user_role, role_authority, redis_code
from libs.utils import create_validate_code, timestamp_to_strftime
from model import admin_navs, base_navs

crypt_obj = XKcrypt()
login_blue = Blueprint('login', __name__, template_folder='../../templates',
                       static_folder='../../statices', url_prefix='/yqfadmin')


@login_blue.route('/captcha', methods=['GET'])
def captcha():
    """
    获取图形验证码
    :return:
    """
    try:
        code_img, strs = create_validate_code(size=(135, 41), bg_color=(185, 211, 238), fg_color=(0, 0, 205),
                                              point_chance=4, chars=string.hexdigits)
        buf = StringIO.StringIO()
        code_img.save(buf, 'JPEG', quality=70)
        buf_str = buf.getvalue()
        response = make_response(buf_str)
        # 验证码加密
        ver_code = crypt_obj.encrypt(strs.lower())
        # 验证码存redis
        redis_code.set(ver_code, strs.lower(), ex=int(60 * 30))
        # 验证码存cookie
        response.set_cookie('login_code', value=ver_code)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
    except Exception, e:
        print e
    return e


@login_blue.route('/login', methods=['GET', 'POST'])
def _login():
    """
    后台登录页面和接口
    :return:
    """
    # 获取登录IP和城市
    ip, ip_area = get_ip_area()

    if request.method == 'POST':
        try:
            data = request.get_data()
            data = json.loads(data)
            username = data.get('loginname')
            password = data.get('password')
            captcha = data.get('login_code')
        except:
            return jsonify({'code': 201, 'msg': u'参数错误'})
        if not username or not captcha:
            return jsonify({'code': 201, 'msg': u'缺少参数'})
        temp_code = request.cookies.get('login_code')
        s_captcha = crypt_obj.decrypt(temp_code)
        if not s_captcha or captcha.lower() != s_captcha.lower():
            return jsonify({'code': 202, 'msg': u'验证码不正确'})
        user_obj = admin_user.find_one({'username': username})
        if not user_obj:
            return jsonify({'code': 202, 'msg': u'账户信息不正确'})
        if user_obj.get('status') == 1:
            return jsonify({'code': 202, 'msg': u'账号已被封禁，如有疑问请联系管理员'})
        if not check_password_hash(user_obj.get('password'), password):
            return jsonify({'code': 202, 'msg': u'密码不对'})

        default_values = {
            'user_id': str(user_obj.get('_id')),
            'username': username,
            'ip': ip,
            'city': ip_area,
            'created_time': timestamp_to_strftime(time.time())
        }
        login_log.insert_one(default_values)
        session['username'] = username
        user_key = crypt_obj.encrypt(username.encode("utf-8") + '__' + str(int(time.time())))
        redis_admin.set(user_key, username, ex=int(60 * 60 * 24))
        resp = make_response(jsonify({'code': 200, 'msg': u'成功'}))
        resp.set_cookie('admin_key', value=user_key)
        return resp

    return render_template('login/login.html')


@login_blue.route('/logout', methods=['GET'])
def login_out():
    """
    后台退出登录接口
    :return:
    """
    session.pop('username', None)
    resp = make_response(render_template('jump.html'))
    resp.set_cookie('admin_key', value='')
    return resp


@login_blue.route('', methods=['GET'])
@login_check
def layout():
    """
    框架主页
    :return:
    """
    domain_dic = {'': {'name': u'夺宝APP', 'logo': ''}}
    host_domain = request.headers.get('host')
    name = domain_dic.get(host_domain, {}).get('name', u'夺宝APP')
    logo = domain_dic.get(host_domain, {}).get('logo', u'')
    username = session.get('username')
    user_obj = admin_user.find_one({'username': username})
    user_id = str(user_obj.get('_id'))
    del user_obj['_id']
    role_id_list = user_role.find({'user_id': user_id}).distinct('role_id')
    authority_list = []
    role_authority_cur = role_authority.find({'role_id': {'$in': role_id_list}}).sort([('authority', 1)])
    for role_authority_obj in role_authority_cur:
        authority_list.append(role_authority_obj.get('authority'))
    new_navs = copy.deepcopy(base_navs)
    add_navs = []
    for index, nav_obj in enumerate(admin_navs):
        if nav_obj.has_key('children'):
            children_list = nav_obj.get('children')
            for children_obj in children_list:
                try:
                    if filter(lambda x: filter(lambda b: b == x['value'], authority_list),
                              children_obj['authority_list']):
                        new_navs[index]['children'].append(children_obj)
                    else:
                        pass
                except:
                    pass

    last_navs = []
    for item in new_navs:
        if item.get('spread') or item.get('children'):
            last_navs.append(item)
    navs = json.dumps(last_navs)
    nickname = user_obj.get('name', '')
    if not nickname:
        nickname = user_obj.get('username', '')
    user_obj['nickname'] = nickname
    return render_template('layout.html', navs=last_navs, login_obj=user_obj, name=name, logo=logo)


@login_blue.route('/index', methods=['GET'])
@login_check
def index():
    """
    后台首页
    :return:
    """
    return u'欢迎进入夺宝APP后台管理系统'


@login_blue.route('/revise_psw', methods=['GET'])
@login_check
def revise_psw():
    username = session.get('username')
    user_obj = admin_user.find_one({'username': username})
    del user_obj['_id']
    return render_template('login/revise_psw.html', user_obj=user_obj)


@login_blue.route('/update', methods=['post'])
@login_check
def update():
    data = {key: dict(request.form)[key][0] for key in dict(request.form)}
    if not data:
        data = request.get_json()
    username = session.get('username')
    user_obj = admin_user.find_one({'username': username})
    _id = data.get('_id')
    if not _id or not ObjectId.is_valid(_id):
        _obj = user_obj
    else:
        _obj = admin_user.find_one({'_id': ObjectId(_id)})
    if not _obj:
        return jsonify({'code': 202, 'msg': u'不存在'})
    _id = str(_obj.get('_id'))
    if 'old_pass' in data:
        if not check_password_hash(_obj.get('password'), data.get('old_pass')):
            return jsonify({'code': 203, 'msg': u'旧密码不正确'})
        _values = data.get('password')
        _values = generate_password_hash(_values)
        if _obj.get('password') != _values:
            admin_user.update_one({'_id': ObjectId(_id)}, {'$set': {'password': _values}})
    return jsonify({'code': 200, 'msg': u'成功'})


@login_blue.route('/login_log', methods=['GET'])
@login_check
def _login_log():
    """
    登录日志页面
    :return:
    """
    username = session.get('username')
    user_obj = admin_user.find_one({'username': username})
    del user_obj['_id']
    return render_template('login/login_log.html', user_obj=user_obj)


@login_blue.route('/login/my_list', methods=['get'])
@login_check
def my_list():
    username = session.get('username')
    criteria = {'username': username}
    try:
        page_num = int(request.args.get('page_num', 1)) - 1
        limit = int(request.args.get('limit', 20))
    except:
        return jsonify({'code': 201, 'msg': u'参数错误'})

    _cur = login_log.find(criteria)
    _count = _cur.count()
    if _count % limit:
        num = _count / limit + 1
    else:
        num = _count / limit
    if _count > (page_num * limit):
        _list = []
        cur_list = _cur.sort([('_id', -1)]).skip(page_num * limit).limit(limit)
        for _obj in cur_list:
            try:
                _obj['_id'] = str(_obj['_id'])
                _list.append(_obj)
            except Exception, e:
                print e
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': _list}})
    else:
        return jsonify({'code': 200, 'data': {'num': num, 'count': _count, 'page': page_num + 1, 'list': []}})
