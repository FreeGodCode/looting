# -*- coding: utf8 -*-

# ---------------- 系统、扩展库----------------
import hashlib
import json
import os
import platform
import random
import re
import threading
import time
import uuid
from datetime import datetime
from multiprocessing import Pool

import jpush
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider

import SendSmsRequest
from conf import conf
from db import redis_ip
from db import system, redis_code
from qiniu_api import qiniu_upload_file

path = os.getcwd()


def get_proxies():
    """
    从代理IP池里获取一个代理IP
    :return:
    """
    # 优先获取优质代理IP
    proxy = redis_ip.brpop('high', timeout=1)
    if not proxy:
        # 获取普通代理IP，并且会一直等待有IP才继续
        proxy = redis_ip.brpop('normal', timeout=0)
    proxy_ = proxy[1].split(':')
    ip = proxy_[0]
    port = proxy_[1]
    proxies = {
        "http": "http://{0}:{1}".format(ip, port),
        "https": "http://{0}:{1}".format(ip, port),
    }
    return proxies, proxy[1]


dict_number = {
    '0': u'O',
    '1': u'一',
    '2': u'二',
    '3': u'三',
    '4': u'四',
    '5': u'五',
    '6': u'六',
    '7': u'七',
    '8': u'八',
    '9': u'九'
}

chars = ''.join((''.join(map(str, range(10)))))

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'ico'])


def create_validate_code(size=(120, 30),
                         chars=chars,
                         mode='RGB',
                         bg_color=(255, 200, 0),
                         fg_color=(255, 0, 0),
                         font_size=21,
                         font_type='arialbi.ttf',
                         length=4,
                         draw_points=True,
                         point_chance=2):
    """
    :param size: 图片的大小，格式（宽，高），默认为(120, 30)
    :param chars: 允许的字符集合，格式字符串
    :param mode: 图片模式，默认为RGB
    :param bg_color: 背景颜色，默认为白色
    :param fg_color: 前景色，验证码字符颜色
    :param font_size:验证码字体大小
    :param font_type: 验证码字体，默认为 Monaco.ttf
    :param length: 验证码字符个数
    :param draw_points: 是否画干扰点
    :param point_chance: 干扰点出现的概率，大小范围[0, 50]
    :return:
    """
    width, height = size
    img = Image.new(mode, size, bg_color)  # 创建图形
    draw = ImageDraw.Draw(img)  # 创建画笔
    if draw_points:
        # 绘制干扰点
        chance = min(50, max(0, int(point_chance)))  # 大小限制在[0, 50]
        # for w in xrange(width):
        for w in range(width):
            # for h in xrange(height):
            for h in range(height):
                tmp = random.randint(0, 50)
                if tmp > 50 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    # 绘制验证码字符
    c_chars = get_chars(chars, length)
    strs = '%s' % ''.join(c_chars)
    if 'Linux' in platform.system():
        font_type = '/usr/share/fonts/arialbi.ttf'
    font = ImageFont.truetype(font_type, font_size)
    font_width, font_height = font.getsize(strs)
    draw.text(((width - font_width) / 3, (height - font_height) / 4), strs, font=font, fill=fg_color)

    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100, 0, 0, 0, 1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500, 0.001, float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）
    return img, strs


# def create_threadpool(func, number, args=[]):
def create_threadpool(func, number, *args):
    threadpool = []
    # for i in xrange(number):
    for i in range(number):
        th = threading.Thread(target=func, args=args)
        threadpool.append(th)
    for th in threadpool:
        th.start()
    for th in threadpool:
        threading.Thread.join(th)


# def create_pool(number, func, t_number, args=[]):
def create_pool(number, func, t_number, *args):
    pool = Pool(processes=number)
    for i in range(number):
        pool.apply_async(create_threadpool, (func, t_number, args,))
    pool.close()
    pool.join()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_center_Str(left, right, str):
    """
    根据左右标记截取字符串部分字符
    :param left:左侧字符串标记
    :param right:右侧字符串标记
    :param str:被截取的字符串
    :return:截取后的字符串
    """
    s = re.compile(left + '(\S*?)' + right).search(str)
    try:
        return s.group(1)
    except:
        return ''


def get_center_str(left, right, str):
    """
    根据左右标记截取字符串部分字符
    :param left:左侧字符串标记
    :param right:右侧字符串标记
    :param str:被截取的字符串
    :return:截取后的字符串
    """
    s = re.compile(left + '(.|[\s\S]*?)' + right).search(str)
    try:
        return s.group(1)
    except:
        return ''


def get_center_str_all(left, right, str):
    """
    根据左右标记截取所有符合的字符
    :param left:左侧字符串标记
    :param right:右侧字符串标记
    :param str:被截取的字符串
    :return:截取后的字符串集合
    """
    try:
        return re.compile(left + '(.|[\s\S]*?)' + right).findall(str)
    except:
        return []


def get_center_str_all_s(left, right, str):
    """
    根据左右标记截取所有符合的字符
    :param left:左侧字符串标记
    :param right:右侧字符串标记
    :param str:被截取的字符串
    :return:截取后的字符串集合
    """
    try:
        return re.compile(left + '(\S*?)' + right).findall(str)
    except:
        return []


def filter_html(html):
    """
    过滤字符串中的所有html标记
    :param html: 要过滤的字符串
    :return: 过滤后的字符串
    """
    try:
        return re.sub(r'<[^>]+>', '', html)
    except Exception as e:
        return html


def get_chars(chars, length):
    """
    生成给定长度的字符串，返回列表格式

    :param chars: 允许的字符集合，格式字符串
    :param length: 字符串长度
    :return:
    """
    return random.sample(chars, length)


def get_chars2(type_num, length):
    """
    生成给定长度的字符串，返回列表格式

    :param type_num: 1允许的字符集合，格式字符串
    :param length: 字符串长度
    :return:
    """
    if type_num == 0:
        chars = '0123456789'
    else:
        chars = 'abcdefghijklmnpqrstuvwxyz123456789'
    return ''.join(random.sample(chars, length))


def random_str(randomlength):
    """
    生成随机字母和数字字符串

    :param num: 随机数的数量
    :return: 返回指定数量的随机数，不包含 0
    """
    str = ''
    chars = 'abcdefghijklmnpqrstuvwxyz0123456789'
    length = len(chars) - 1
    rdm = random.Random()
    for i in range(randomlength):
        str += chars[rdm.randint(0, length)]
    return str


def builder_random(num):
    """
    生成随机数
    :param num: 随机数的数量
    :return: 返回指定数量的随机数
    """
    sjs = ''
    for i in range(num):
        ri = random.randint(0, 9)
        sjs += str(ri)
    return sjs


def md5(pw):
    """
    字符串转md5
    :param pw:明文字符串
    :return: 返回md5字符串
    """
    if not pw:
        return ''
    m2 = hashlib.md5()
    m2.update(pw.encode("utf8"))
    return m2.hexdigest()


def query_to_dict(query):
    """
    query转为字典
    :param query: param1=value1&param2=value2
    :return:
    {
        "param1": "value1",
        "params2": "value2"
    }
    """
    params = {}
    if query is None or query == '':
        return params
    if query.find('&') == -1:
        return False
    splits = query.split('&')
    for s in splits:
        k, v = s.split('=')
        params[k] = v
    return params


def dict_to_query(data):
    """
    字典转为查询字符串
    :param data: {
                    "param1": "value1",
                    "params2": "value2"
                }
    :return: param1=value1&param2=value2
    """
    if data is None or data == {}:
        return ''
    sorted_params = sorted(data.iteritems(), key=lambda e: e[0])
    temp = []
    for k, v in sorted_params:
        temp.append('='.join([k, str(v)]))
    query = '&'.join(temp)
    return query


def unix_time_to_string(unix_time=None, format='%Y-%m-%d %H:%M:%S'):
    """
    unix时间戳转字符串时间
    :param unix_time:unix时间戳
    :param format:字符串时间格式
    :return:转换后的字符串
    """
    if not unix_time:
        unix_time = time.time()
    return time.strftime(format, time.localtime(unix_time))


def timestamp_to_strftime(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """
    时间戳转日期
    timestamp：要转换的时间戳
    format：日期格式化字符串

    :return 返回日期格式字符串
    """
    ltime = time.localtime(timestamp)
    time_str = time.strftime(format, ltime)
    return time_str


def multi_get_letter(str_input):
    if isinstance(str_input, str):
        unicode_str = str_input
    else:
        try:
            unicode_str = str_input.decode('utf8')
        except:
            try:
                unicode_str = str_input.decode('gbk')
            except:
                print('unknown coding')
                return
    return_list = []
    for one_unicode in unicode_str:
        return_list.append(single_get_first(one_unicode))
    return return_list


def single_get_first(unicode1):
    str1 = unicode1.encode('gbk')
    try:
        ord(str1)
        return str1
    except:
        asc = ord(str1[0]) * 256 + ord(str1[1]) - 65536
        if asc >= -20319 and asc <= -20284:
            return 'a'
        if asc >= -20283 and asc <= -19776:
            return 'b'
        if asc >= -19775 and asc <= -19219:
            return 'c'
        if asc >= -19218 and asc <= -18711:
            return 'd'
        if asc >= -18710 and asc <= -18527:
            return 'e'
        if asc >= -18526 and asc <= -18240:
            return 'f'
        if asc >= -18239 and asc <= -17923:
            return 'g'
        if asc >= -17922 and asc <= -17418:
            return 'h'
        if asc >= -17417 and asc <= -16475:
            return 'j'
        if asc >= -16474 and asc <= -16213:
            return 'k'
        if asc >= -16212 and asc <= -15641:
            return 'l'
        if asc >= -15640 and asc <= -15166:
            return 'm'
        if asc >= -15165 and asc <= -14923:
            return 'n'
        if asc >= -14922 and asc <= -14915:
            return 'o'
        if asc >= -14914 and asc <= -14631:
            return 'p'
        if asc >= -14630 and asc <= -14150:
            return 'q'
        if asc >= -14149 and asc <= -14091:
            return 'r'
        if asc >= -14090 and asc <= -13119:
            return 's'
        if asc >= -13118 and asc <= -12839:
            return 't'
        if asc >= -12838 and asc <= -12557:
            return 'w'
        if asc >= -12556 and asc <= -11848:
            return 'x'
        if asc >= -11847 and asc <= -11056:
            return 'y'
        if asc >= -11055 and asc <= -9000:
            return 'z'
        return ''


def get_first_letter(str_input):
    a = multi_get_letter(str_input)
    b = ''
    for i in a:
        b = b + i
    return b


def create_thread(func, *args):
    """
    创建一个线程
    :return:
    """
    t = threading.Thread(target=func, args=args)
    t.daemon = True
    t.start()
    return True


def upload_img(file_obj):
    _obj = system.find_one({})
    qn_url = _obj.get('qn_url', '')
    bucket_name = _obj.get('bucket_name', '')
    access_key = _obj.get('access_key', '')
    secret_key = _obj.get('secret_key', '')
    if qn_url and bucket_name and access_key and secret_key:
        fname = datetime.now().strftime(format='%Y%m%d%H%M%S') + '-' + random_str(4) + '.jpg'
        add_img_url = qiniu_upload_file(fname, file_obj.stream, qn_url=qn_url, bucket_name=bucket_name,
                                        access_key=access_key, secret_key=secret_key)
        if add_img_url:
            return True, add_img_url
    return False, ''


# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"

acs_client = AcsClient(conf.ACCESS_KEY_ID, conf.ACCESS_KEY_SECRET, REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)


def send_sms_aliy(phone_numbers, sign_name, template_code, template_param=None):
    """

    :param phone_numbers: 需要发送的电话号码
    :param sign_name: 短信模板签名
    :param template_code: 模板代码
    :param template_param: 模板参数
    :return:
    """
    business_id = uuid.uuid1()
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)
    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)
    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)
    # 短信签名
    smsRequest.set_SignName(sign_name)
    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)
    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)
    response_json = json.loads(smsResponse)
    return response_json


_jpush = jpush.JPush(conf.jp_app_key, conf.jp_secret)


# 极光发送通知方法
def jp_notification(alert, big_text, k1, v1, type_num=0, jg_ids=[]):
    push = _jpush.create_push()
    if jg_ids:
        push.audience = {'registration_id': jg_ids}
    else:
        push.audience = jpush.all_
    push.platform = jpush.all_
    ios = jpush.ios(alert=alert, sound="a.caf", extras={k1: v1, 'type': type_num})
    android = jpush.android(alert=alert.get('body'), title=alert.get('title'), priority=1, style=1, alert_type=1,
                            big_text=big_text, extras={k1: v1, 'type': type_num})
    push.notification = jpush.notification(alert=alert, android=android, ios=ios)
    result = push.send()
    return result


# 微信公众号发送通知模板
def push_template(*args):
    access_token = redis_code.get('access_token')
    if not access_token:
        system_obj = system.find_one({})

        AppSecret = system_obj.get('gzh_appsecret')
        AppID = system_obj.get('gzh_appid')
        token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(
            AppID, AppSecret)
        res = requests.get(url=token_url)
        res_json = res.json()
        access_token = res_json.get('access_token')
        if access_token:
            expires_in = res_json.get('expires_in')
            redis_code.set('access_token', access_token, ex=(expires_in - 600))
    openid = args[0]
    template_id = args[1]
    first = args[2]
    keyword1 = args[3]
    keyword2 = args[4]
    keyword3 = args[5]
    # 提现成功通知
    if template_id in ['KNteD66yN8I3uL4ObD2jZJn3py74Uezn2WeImEFwkkI', 'wuVWd1zIgtki7iNGh5a3Dq-wQzKbPCdBjkptsEVz0GM']:

        post_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)
        post_data = {
            "touser": openid,
            "template_id": template_id,

            "data": {
                "first": {
                    "value": u'您好，{0}结果如下'.format(first),
                    "color": "#173177"
                },
                "keyword1": {
                    "value": keyword1,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": u'已通过',
                    "color": "#173177"
                },
                "keyword3": {
                    "value": u'十秒到账，请注意查收',
                    "color": "#173177"
                }
            }
        }
        res = requests.post(url=post_url, data=json.dumps(post_data))
        if res.json().get('errcode') == 0:
            pass
    # 提现失败通知
    elif template_id in ['UknWg_f71WRhYNjm-dr4JPacykJX0ZkeXddphUtFcHc', '-FAS2kf4aKbhBkVndi-LO28t4EMVupH-eMOxkB1iCBM']:
        post_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)
        post_data = {
            "touser": openid,
            "template_id": template_id,

            "data": {
                "first": {
                    "value": u'您好，您的{0}失败了，请进入热量星球APP中查看修改'.format(first),
                    "color": "#173177"
                },
                "keyword1": {
                    "value": keyword1,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": keyword2,
                    "color": "#173177"
                },
                "keyword3": {
                    "value": keyword3,
                    "color": "#173177"
                }
            }
        }
        res = requests.post(url=post_url, data=json.dumps(post_data))
        if res.json().get('errcode') == 0:
            pass
    # 成为星主通知
    elif template_id in ['BicMMuwBiTojbCEGRocNevHJfYhibNYBHP_ieScf7KI', 'i5zbssHtNl1LrjER49z6Yaz18DgRODJGwz4T72bYMA8']:
        post_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)
        post_data = {
            "touser": openid,
            "template_id": template_id,

            "data": {
                "first": {
                    "value": u'您好，恭喜您创建了属于您自己的星球，进入热量星球APP可查看您的分润......',
                    "color": "#173177"
                },
                "keyword1": {
                    "value": keyword1,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": keyword2,
                    "color": "#173177"
                },
                "keyword3": {
                    "value": u'星主',
                    "color": "#173177"
                }
                # "remark": {
                #     "value": u'恭喜您创建属于您自己的星球，进入APP查看你的分润......',
                #     "color": "#173177"
                # }
            }
        }
        res = requests.post(url=post_url, data=json.dumps(post_data))
        if res.json().get('errcode') == 0:
            pass
    # 第一笔分润通知
    elif template_id in ['kLvKUoi6_y_rB4CN1MBt3956Gh54_AkfxzItmH6yQtA', 'CuRkLGY-RCH-CZfxHnuQXEmAqm7Q1tvcDXJSwWUV0NY']:
        post_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)
        post_data = {
            "touser": openid,
            "template_id": template_id,
            "data": {
                "first": {
                    "value": u'您好，您有一笔分润已到账',
                    "color": "#173177"
                },
                "keyword1": {
                    "value": keyword1,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": keyword2,
                    "color": "#173177"
                },
                "keyword3": {
                    "value": keyword3,
                    "color": "#173177"
                }
            }
        }
        res = requests.post(url=post_url, data=json.dumps(post_data))
        if res.json().get('errcode') == 0:
            pass
    # 整点红包通知
    elif template_id in ['HOnVZPwa-cf9JCr5dzWNQA9QyoPZEexSsKU1YzQsQPY', 'uYbaifuTdV5t3w-vXXibloAMV_ueYzHfY890RIXFHEI']:
        post_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)
        post_data = {
            "touser": openid,
            "template_id": template_id,
            "data": {
                "first": {
                    "value": u'您好，整点红包马上要开始啦！',
                    "color": "#173177"
                },
                "keyword1": {
                    "value": u'整点抢红包',
                    "color": "#173177"
                },
                "keyword2": {
                    "value": keyword2,
                    "color": "#173177"
                },
                "remark": {
                    "value": keyword3,
                    "color": "#173177"
                }
            }
        }
        res = requests.post(url=post_url, data=json.dumps(post_data))
        if res.json().get('errcode') == 0:
            pass
    # 余额提现唤醒
    elif template_id in ['WgNk3x4EYRwMz853p-vl9TPxRS6GRGzEqjpN7aIcbD0', 'jdaV3MHHoiqFfSrgZp2qR4JQC5Toj4u3QTtMOgp5igA']:
        post_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)
        post_data = {
            "touser": openid,
            "template_id": template_id,
            "data": {
                "first": {
                    "value": u'您好，您的账号余额还有{0}元待提现'.format(first),
                    "color": "#173177"
                },
                "keyword1": {
                    "value": keyword1,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": keyword2,
                    "color": "#173177"
                },
                "remark": {
                    "value": u'请及时登录App，对账户余额进行提现。',
                    "color": "#173177"
                }
            }
        }
        res = requests.post(url=post_url, data=json.dumps(post_data))
        if res.json().get('errcode') == 0:
            pass


def gen_signature(secretKey, params=None):
    """生成签名信息
    网易云短信
    Args:
        secretKey 产品私钥
        params 接口请求参数，不包括signature参数
    """
    params_str = ""
    for k in sorted(params.keys()):
        params_str += str(k) + str(params[k])
    params_str += secretKey
    return hashlib.md5(params_str).hexdigest()


def send_sms_163(mobile, params, templateId):
    """
    能用接口发短信
    """
    try:
        sms_send_uri = "https://sms.dun.163yun.com/v2/sendsms"
        data = {'secretId': '8a772aa8e6ea1fba125c4f4aba6153e6', 'businessId': '77e87b801a494787a9bf829856d13419',
                'version': 'v2', 'timestamp': int(time.time() * 1000), 'nonce': get_chars2(1, 10), 'mobile': mobile,
                'templateId': templateId, 'params': params, 'paramType': 'json'}
        signature = gen_signature('819d41c0540215ffe9486570f8e77e05', data)
        data['signature'] = signature

        response = requests.post(url=sms_send_uri, data=data, timeout=30)
        response_json = response.json()
        return response_json
    except Exception as e:
        print(e)
        return {'code': 201}


def generate_dwz(Url):
    """
    通过百度api 生成短网址
    :param Url:
    :return:
    """
    host = 'https://dwz.cn'
    path = '/admin/v2/create'
    url = host + path

    content_type = 'application/json'

    token = '4d8bef78cd3280a1e2e689199aeb550c'

    bodys = {'Url': Url, 'TermOfValidity': 'long-term'}

    # 配置headers
    headers = {'Content-Type': content_type, 'Token': token}

    # 发起请求
    response = requests.post(url=url, data=json.dumps(bodys), headers=headers)
    req_josn = json.loads(response.text)

    if req_josn.get('Code') == 0:
        return req_josn.get('ShortUrl')
    return ''


def generate_tcn(Url):
    """
    通过http://api.t.sina.com.cn/short_url/shorten.json  生成短网址

    :param Url:
    :return:
    """

    params = {
        'url': Url,
        'shortUrl': 'tcn'
    }
    response = requests.get(url='https://api.ooopn.com/dwz/api.php', params=params)
    req_josn = response.json()

    if req_josn.get('tcn', '').find('http') > -1:
        return req_josn.get('tcn', '')
    url_short = ''
    host = 'http://api.t.sina.com.cn/short_url/shorten.json'
    source_list = ['3925598208', '3271760578', '31641035', '2815391962']

    for source in source_list:
        params = {
            'url_long': Url,
            'source': source
        }
        # 发起请求
        response = requests.get(url=host, params=params)
        req_josn = response.json()
        if req_josn:
            if req_josn[0].get('url_short') != Url:
                url_short = req_josn[0].get('url_short')
                break

    return url_short


def get_now_part(format_str):
    return get_datetime_part(datetime.now(), format_str)


def get_datetime_part(datetime_val, format_str):
    return datetime.strptime(datetime_val.strftime(format_str), format_str)


if __name__ == '__main__':
    print(generate_tcn('http://sms.yiqifu88.com/'))
