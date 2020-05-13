# -*- coding: utf8 -*-
import Queue

import pymongo
import redis

from conf import conf

conn = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}/'.format(conf.DB_UN, conf.DB_PW, conf.DB_HOST, conf.DB_PORT))

conn_db = conn[conf.DB_NAME]

admin_user = conn_db['admin_user']
role = conn_db['role']
user_role = conn_db['user_role']
role_authority = conn_db['role_authority']
system = conn_db['system']
# 运营参数配置
operation = conn_db['operation']
# 昨日收益 分红配置
dividend_config = conn_db['dividend_config']
# 整点红包
integer_red = conn_db['integer_red']
# 整点红包详情
integer_red_detail = conn_db['integer_red_detail']
# 整点红包订阅通知
integer_red_subscribe = conn_db['integer_red_subscribe']
# 猜红包
guess_red = conn_db['guess_red']
# 猜红包详情
guess_red_detail = conn_db['guess_red_detail']
login_log = conn_db['login_log']
# 请求日志
req_log = conn_db['req_log']
# 异常请求日志
deviant_log = conn_db['deviant_log']
# 错误日志
error_log = conn_db['error_log']
# 请求ip 统计
req_ip_statistical = conn_db['req_ip_statistical']

user = conn_db['user']
user_offline_pullup = conn_db['user_offline_pullup']
# 邀请码列表
earth_code = conn_db['earth_code']
# 手机注册表
reg_user = conn_db['reg_user']
# 用户意见反馈
feedback = conn_db['feedback']
calorific_record = conn_db['calorific_record']
# 我的红包记录

red_record = conn_db['red_record']
# 星球 分润 记录
commission_record = conn_db['commission_record']
invite_code_data = conn_db['invite_code_data']
task2_code_data = conn_db['task2_code_data']

# 素材轮播
carousel = conn_db['carousel']
# 弹框通知
bulletin_notice = conn_db['bulletin_notice']
# 站内消息通知
station_notice = conn_db['station_notice']
# 文档
help_center = conn_db['help_center']
# 首页广告
home_ad = conn_db['home_ad']
# 红包玩法
redbag_game = conn_db['redbag_game']
# 星球默认头像
planet_img = conn_db['planet_img']
# 热量任务模板列表
heat_task = conn_db['heat_task']
# app唤醒任务
app_wake_task = conn_db['app_wake_task']
# 日常任务
daily_task = conn_db['daily_task']

# 日数据统计
statistical_day = conn_db['statistical_day']
# 广告数据统计
ad_statistical_day = conn_db['ad_statistical_day']
# 官方邀请数据统计
statistical_day_official = conn_db['statistical_day_official']
# 用户在线时长统计
s_user_online_t = conn_db['s_user_online_t']
# 落角页域名 
domain_h5 = conn_db['domain_h5']
# 版本列表
version_manag = conn_db['version_list']
# 绑定微信提现码
cash_code_data = conn_db['cash_code_data']
# 总的排行榜
leaderboard = conn_db['leaderboard']
leaderboard_withdraw = conn_db['leaderboard_withdraw']

invite_activity_data = conn_db['invite_activity_data']

# 商品
product = conn_db['product']
# 订单
order = conn_db['order']
# 每日上新
daily_new_template = conn_db['daily_new_template']
daily_new = conn_db['daily_new']
daily_new_record = conn_db['daily_new_record']
# 秒杀
flash_sale_template = conn_db['flash_sale_template']
flash_sale = conn_db['flash_sale']
flash_sale_record = conn_db['flash_sale_record']

# 奖品记录
prize_record = conn_db['prize_record']
# temp
db_temp = conn_db['db_temp']

# 邀请人表
invite_user = conn_db['invite_user']

# 每日上新号码
daily_new_code = conn_db['daily_new_code']

# 每日签到
daily_attendance = conn_db['daily_attendance']

# 收益历史
income = conn_db['income']

# 通知信息
notify_msg = conn_db['notify_msg']

# 我的提现记录
withdraw_record = conn_db['withdraw_record']

# 我的提现订单
withdraw_order = conn_db['withdraw_order']

# 任务事件配置
task_event = conn_db['task_event']

# 用户任务表
user_task = conn_db['user_task']

# -------------------------------------------------------------------

CONFIG_TYPE_DAILY_ATTENDANCE = 10001
CONFIG_TYPE_DAILY_NEW = 10002
CONFIG_TYPE_FLASH_SALE = 10003
CONFIG_TYPE_INVITE_REWARD = 10010
CONFIG_TYPE_DIVIDEND = 10011
CONFIG_TYPE_USER_LEVEL = 10012
CONFIG_TYPE_TOP_TASK = 10013
CONFIG_TYPE_NEW_USER = 10015
CONFIG_TYPE_INVITE_TASK = 10016

CONFIG_TYPE_APP_ROUTE = 10100

CONFIG_TYPE_WITHDRAW = 10200
CONFIG_TYPE_WITHDRAW_OPTION = 10201
CONFIG_TYPE_WITHDRAW_CLASS = 10202
# 配置储存库
configs = conn_db['configs']


def create_redis_conn(db_num):
    """
    创建 redis 数据库连接

    :param db_num: 数据库编号
    :return: 返回公众号 redis 处理的对象
    """
    pool_ = redis.ConnectionPool(host=conf.R_HOST,
                                 port=conf.R_PORT,
                                 password=conf.R_AUTH,
                                 db=db_num,
                                 retry_on_timeout=True)
    redis_client = redis.Redis(connection_pool=pool_)
    return redis_client


# 后台图片验证码
redis_code = create_redis_conn(0)
# 后台管理员用户token 验证库
redis_admin = create_redis_conn(1)
# 代理ip 池
redis_ip = create_redis_conn(2)
# 七牛错误记录
redis_error = create_redis_conn(3)
# 任务第二步奖励码队列
redis_task2_code = create_redis_conn(4)
# 用户邀请码队列
redis_invite_code = create_redis_conn(5)
# 提现任务队列
withdraw_task_code = create_redis_conn(6)
# 请求日志队列
redis_req_log = create_redis_conn(14)
# 业务配置
redis_config = create_redis_conn(15)

log_q = Queue.Queue()
