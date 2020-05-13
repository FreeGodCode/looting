# -*- coding: utf8 -*-


from flask import Blueprint, render_template
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMaterial

from libs.common import login_check
from libs.db import system

system_obj = system.find_one()
if system_obj:
    wechat_config = WeChatClient(appid=system_obj.get('gzh_appid'), secret=system_obj.get('gzh_appsecret'),
                                 access_token=system_obj.get('gzh_token'))
system_blue = Blueprint('system', __name__, template_folder='../../templates', static_folder='../../statices',
                        url_prefix='/system')


@system_blue.route('/edit', methods=['get'])
@login_check
def eidt():
    return render_template('system/sys_set.html')


@system_blue.route('/create_menu', methods=['GET'])
@login_check
def create_menu():
    """
    微信公众号菜单创建

    :return: ok 表示菜单创建成功
    """
    menu_button0 = {
        'type': 'click',
        'name': u'领取奖励',
        'key': 'receiveaward'
    }
    menu_button1 = {
        'name': u'下载APP',
        'type': 'view',
        'url': 'http://api.yiqifu88.com/h5/download'
    }
    menu_button2 = {
        'name': u'关于我们',
        'sub_button': [
            {
                'type': 'view',
                'name': u'关于热量',
                'url': 'http://api.yiqifu88.com/heat/tutorial'
            },
            {
                'type': 'view',
                'name': u'关于星球',
                'url': 'http://api.yiqifu88.com/home/tutorial'
            },
            {
                'type': 'view',
                'name': u'联系我们',
                'url': 'http://api.yiqifu88.com/help/about'
            }, {
                'type': 'click',
                'name': u'企业微信',
                'key': 'enterpriseWeChat'
            }]}
    #         # {
    #         #     'type': 'click',
    #         #     'name': u'商务合作',
    #         #     'key': 'business'
    #         # }
    #     ]
    # }
    menu_data = dict()
    menu_data['button'] = [menu_button0, menu_button1, menu_button2]  # , menu_button3]
    wechat_config.menu.create(menu_data)
    return 'ok!'


def get_image_id_list():
    WeChatMaterial_obj = WeChatMaterial(wechat_config)
    a = WeChatMaterial_obj.batchget('image')
    print a
