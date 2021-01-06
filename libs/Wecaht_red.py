# -*- coding: utf-8 -*-


import platform
import sys
from uuid import uuid4
from xml.etree import ElementTree

import requests

from conf import conf
from utils import md5

# reload(sys)
# sys.setdefaultencoding('utf-8')

if 'Linux' in platform.system():
    WEIXIN_PAY_CERT_PATH = '/root/planet_back/cert/apiclient_cert.pem'
    WEIXIN_PAY_CERT_KEY_PATH = '/root/planet_back/cert/apiclient_key.pem'
else:
    WEIXIN_PAY_CERT_PATH = 'D:\\code\\planet_back\\cert\\apiclient_cert.pem'
    WEIXIN_PAY_CERT_KEY_PATH = 'D:\\code\\planet_back\\cert\\apiclient_key.pem'
SENDREDPACK_URL = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'
SENDGROUPREDPACK_URL = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendgroupredpack'
PAYMKTTRANSFERS_URL = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'


def sign(params):
    '''
    https://pay.weixin.qq.com/wiki/doc/api/tools/cash_coupon.php?chapter=4_3
    '''
    params = [(str(key), str(val)) for key, val in params.iteritems() if val]
    sorted_params_string = '&'.join('='.join(pair) for pair in sorted(params))
    sign = '{}&key={}'.format(sorted_params_string, conf.WEIXIN_PAY_API_KEY)
    return md5(sign).upper()


def get_req_xml(params):
    """拼接XML
    """
    xml = "<xml>"
    for k, v in params.items():
        v = str(v).encode('utf8')
        k = k.encode('utf8')
        xml += '<' + k + '><![CDATA[' + v + ']]></' + k + '>'
    xml += "</xml>"
    return xml


def sendredpack(re_openid='', total_amount=0,
                total_num=1, send_name=u'热量星球提现', mch_billno=None,
                wishing=u'热量星球抢红包、赚红包，提现秒到账', act_name=u'抢红包、赚红包', remark=u'抢越多得越多，每天都有抢',
                client_ip='113.87.130.21'):
    randuuid = uuid4()
    nonce_str = str(randuuid).replace('-', '')
    mch_id = conf.WEINXIN_PAY_MCH_ID
    wxappid = conf.WEIXIN_APP_ID
    if not mch_billno:
        return False

    params = {
        'mch_billno': mch_billno,
        'mch_id': mch_id,
        'wxappid': wxappid,
        'send_name': send_name,
        're_openid': re_openid,
        'total_amount': total_amount,
        'total_num': total_num,
        'wishing': wishing,
        'client_ip': client_ip,
        'act_name': act_name,
        'remark': remark,
        'nonce_str': nonce_str,
    }
    if total_amount < 100 or total_amount > 2000:
        params['scene_id'] = 'PRODUCT_2'

    sign_string = sign(params)
    params['sign'] = sign_string

    content = get_req_xml(params)
    headers = {'Content-Type': 'application/xml'}

    respose = requests.post(SENDREDPACK_URL, data=content, headers=headers,
                            cert=(WEIXIN_PAY_CERT_PATH, WEIXIN_PAY_CERT_KEY_PATH))
    try:
        print(respose.text.encode('utf8'))
    except:
        pass
    re_xml = ElementTree.fromstring(respose.text.encode('utf8'))
    xml_status = re_xml.getiterator('return_code')[0].text
    if xml_status != 'SUCCESS':
        return False, re_xml.getiterator('return_msg')[0].text
    result_code = re_xml.getiterator('result_code')[0].text
    if result_code != 'SUCCESS':
        return False, re_xml.getiterator('err_code')[0].text
    try:
        return True, re_xml.getiterator('send_listid')[0].text
    except:
        return True, 'SUCCESS'


def sendgroupredpack(re_openid='', total_amount=0,
                     total_num=1, send_name=u'热量星球提现', mch_billno=None,
                     wishing=u'热量星球抢红包、赚红包，提现秒到账', act_name=u'抢红包、赚红包', remark=u'抢越多得越多，每天都有抢',
                     client_ip='113.87.130.21'):
    randuuid = uuid4()
    nonce_str = str(randuuid).replace('-', '')
    mch_id = conf.WEINXIN_PAY_MCH_ID
    wxappid = conf.WEIXIN_APP_ID
    if not mch_billno:
        return False

    params = {
        'mch_billno': mch_billno,
        'mch_id': mch_id,
        'wxappid': wxappid,
        'send_name': send_name,
        're_openid': re_openid,
        'total_amount': total_amount,
        'total_num': total_num,
        'wishing': wishing,
        'client_ip': client_ip,
        'act_name': act_name,
        'amt_type': 'ALL_RAND',
        'remark': remark,
        'nonce_str': nonce_str,
    }
    if total_amount < 100 or total_amount > 2000:
        params['scene_id'] = 'PRODUCT_2'

    sign_string = sign(params)
    params['sign'] = sign_string

    content = get_req_xml(params)
    headers = {'Content-Type': 'application/xml'}

    respose = requests.post(SENDGROUPREDPACK_URL, data=content, headers=headers,
                            cert=(WEIXIN_PAY_CERT_PATH, WEIXIN_PAY_CERT_KEY_PATH))
    re_xml = ElementTree.fromstring(respose.text.encode('utf8'))
    xml_status = re_xml.getiterator('return_code')[0].text
    if xml_status != 'SUCCESS':
        return False, re_xml.getiterator('return_msg')[0].text
    result_code = re_xml.getiterator('result_code')[0].text
    if result_code != 'SUCCESS':
        return False, re_xml.getiterator('err_code')[0].text
    return True, 'SUCCESS'


def paymkttransfers(re_openid='', total_amount=0, mch_billno=None, wishing=u'热量星球抢红包、赚红包，提现秒到账',
                    client_ip='113.87.130.21', check_name='NO_CHECK', re_user_name=''):
    randuuid = uuid4()
    nonce_str = str(randuuid).replace('-', '')
    mch_id = conf.WEINXIN_PAY_MCH_ID
    wxappid = conf.WEIXIN_APP_ID
    if not mch_billno:
        return False

    params = {
        'partner_trade_no': mch_billno,
        'mchid': mch_id,
        'mch_appid': wxappid,
        'check_name': check_name,
        're_user_name': re_user_name,
        'openid': re_openid,
        'amount': total_amount,
        'desc': wishing,
        'spbill_create_ip': client_ip,
        'nonce_str': nonce_str,
    }

    sign_string = sign(params)
    params['sign'] = sign_string

    content = get_req_xml(params)
    headers = {'Content-Type': 'application/xml'}

    respose = requests.post(PAYMKTTRANSFERS_URL, data=content, headers=headers,
                            cert=(WEIXIN_PAY_CERT_PATH, WEIXIN_PAY_CERT_KEY_PATH))
    try:
        print(respose.text.encode('utf8'))
    except:
        pass
    re_xml = ElementTree.fromstring(respose.text.encode('utf8'))
    xml_status = re_xml.getiterator('return_code')[0].text
    if xml_status != 'SUCCESS':
        return False, re_xml.getiterator('return_msg')[0].text
    result_code = re_xml.getiterator('result_code')[0].text
    if result_code != 'SUCCESS':
        return False, re_xml.getiterator('err_code')[0].text
    try:
        return True, re_xml.getiterator('payment_no')[0].text
    except:
        return True, 'SUCCESS'


if __name__ == '__main__':
    print(paymkttransfers('oOVUCvwftNal7rPFXr8vhIdF44YA', 100, mch_billno='1234567890111111111')[1])
