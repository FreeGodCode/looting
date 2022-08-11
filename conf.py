# -*- coding: utf8 -*-
import os


class Config(object):
    DEBUG = True
    # flask绑定ip
    HOST = '127.0.0.1'
    # flask端口
    PORT = 8081

    # Redis IP地址
    R_HOST = '47.101.67.173'
    # Redis 端口
    R_PORT = 5436
    # Redis 密码
    R_AUTH = 'planet_123_test'

    # # 数据库名
    DB_NAME = 'duobao_db'
    # 数据库IP地址
    DB_HOST = '47.101.67.173'
    # 数据库端口
    DB_PORT = 31962
    # 数据库账号
    DB_UN = 'root'
    # 数据库密码
    DB_PW = 'planet_123_test'
    # 接口请求url
    api_url = 'http://test.api.yiqifu88.cn'
    # 短信账号与密码
    ACCESS_KEY_ID = 'LTAIqDF9lOjDXbgh'
    ACCESS_KEY_SECRET = 'QXVM7cDXV8vh0uX5WfHtBN9a4uu88y'

    # 极光api
    # jp_app_key = '3e0957338ed874a92f45b167'
    # jp_secret = '0e0b4c40cedb98ca985705b6'
    # 极光api
    jp_app_key = 'a9b0943fe77d3122cf393e15'
    jp_secret = '43845e6b133ab29e40576a05'
    # 商户号
    WEIXIN_PAY_API_KEY = 'CAfDoajd19coojE2CAfDoajd19coojE2'
    WEINXIN_PAY_MCH_ID = '1556979601'
    WEIXIN_APP_ID = 'wx6c14c81371950044'


class DevelopConfig(Config):
    """
    开发环境
    """
    # 数据库名
    DB_NAME = 'duobao_db'
    # flask是否开启debug模式
    # DEBUG = False
    # 数据库IP地址
    DB_HOST = '127.0.0.1'
    # 数据库端口
    DB_PORT = 27017
    # 数据库账号
    DB_UN = 'root'
    # 数据库密码
    DB_PW = 'dev_test'
    # Redis IP地址
    R_HOST = '127.0.0.1'
    # Redis 端口
    R_PORT = 6379
    # Redis 密码
    R_AUTH = 'dev_test'
    # 接口请求url
    # api_url = 'http://api.yiqifu88.cn'


class TestingConfig(Config):
    """
    测试环境
    """
    # flask是否开启debug模式

    # 数据库IP地址
    # Redis IP地址
    R_HOST = '127.0.0.1'
    # Redis 端口
    R_PORT = 6380
    # Redis 密码
    R_AUTH = 'duobao_123_test'

    # # 数据库名
    DB_NAME = 'duobao_db'
    # 数据库IP地址
    DB_HOST = '127.0.0.1'
    # 数据库端口
    DB_PORT = 27018
    # 数据库账号
    DB_UN = 'root'
    # 数据库密码
    DB_PW = 'duobao_123_test'
    # 接口请求url
    api_url = 'http://test.api.yiqifu88.cn'

    # R_AUTH = 'duobao_0403_official'
    # DB_PW = 'duobao_0403_official'


class ProductionConfig(Config):
    """
    生产环境
    """
    # flask是否开启debug模式
    DEBUG = False
    # 数据库IP地址
    DB_HOST = '127.0.0.1'
    # 数据库端口
    DB_PORT = 34962
    # 数据库账号
    DB_UN = 'root'
    # 数据库密码
    DB_PW = 'duobao_0403_official'
    # Redis IP地址
    R_HOST = '127.0.0.1'
    # Redis 端口
    R_PORT = 9436
    # Redis 密码
    R_AUTH = 'duobao_0403_official'
    # 接口请求url
    api_url = 'https://duobao-api.yiqifu88.cn'

    WEIXIN_APP_ID = 'wxab10e5608ed0ddda'

    # 极光api
    jp_app_key = 'a9b0943fe77d3122cf393e15'
    jp_secret = '43845e6b133ab29e40576a05'


# 自动判断环境生产config
if os.path.exists('production.conf'):
    conf = ProductionConfig()
    conf_ver = 'conf.ProductionConfig'
    conf_env = u'生产环境'
elif os.path.exists('test.conf'):
    conf = TestingConfig()
    conf_ver = 'conf.TestingConfig'
    conf_env = u'测试环境'
else:
    conf = DevelopConfig()
    conf_ver = 'conf.DevelopConfig'
    conf_env = u'开发环境'
