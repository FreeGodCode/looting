# -*- coding: utf8 -*-
from libs.db import statistical_day

statistical_day_dict = {
    'today_str': u'日期',
    'planet_num': u'星球主总数量',
    "planet_commission_total": u'当前星球主总分润',
    'planet_commission': u'当天星球主分润',
    'user_num_total': u'总的用户量',
    'user_num': u'当天新进用户',
    'user_num_novice_task': u'完成新手任务用户',
    'user_num_invite': u'邀请注册用户',
    'user_red_record': u'领取到红包的用户',
    'red_record_num': u'拆到得红包次数',
    'red_average_num': u'用户平均拆红包次数',
    'user_num_invite_bind': u'邀请注册用户已绑定手机',
    'user_num_active': u'活跃用户数',
    'calorific_num': u'系统当前剩余的总热量',
    'calorific_num_obtain': u'当天所有用户获得的热量',
    'calorific_num_expend': u'当天所有用户消耗的热量',
    'red_num': u'当天所有用户领取的红包值',
    'user_balance_num': u'当天所有用户的总余额',
    'withdraw_num': u'今日提现总额',
}

s_user_online_t_dict = {
    'today_str': u'日期',
    'user_id': u'用户id',
    'length_visit_time': u'在线时长 单位秒',
    'first_visit_time': u'第一次上线时间戳',
    'first_visit_time_h': u'第一次上线在几点',
    'last_visit_time': u'当天最后一次活跃时间戳',
    'req_ip': u'当前用户访问的ip',
    'req_ip_area': u'当前用户访问IP所在地区',
    'mp_system_type': u'用户手机系统',
    'home_ad1': u'首页第一个广告位置点击量',
    'home_ad2': u'首页第二个广告位置点击量',
    'home_ad3': u'首页第三个广告位置点击量',
    'home_ad4': u'首页第四个广告位置点击量'
}

# statistical_day.insert_one({
#     'today_str': u'2019-08-27',
#     'planet_num': 1,
#     'planet_commission': 0,
#     'user_num': 7,
#     'user_num_novice_task': 8,
#     'user_num_invite': 9,
#     'user_num_invite_bind': 10,
#     'user_num_active': 11,
#     'calorific_num_obtain': 12,
#     'calorific_num_expend': 2,
#     'red_num': 4,
#     'user_balance_num': 5,
#     'withdraw_num': 6,
# })

ad_statistical_day_dict = {
    'today_str': u'日期',
    'lottery_num_total': u'首页抽奖点击次数',
    'lottery_num_total1': u'热量页抽奖点击次数',
    'lottery_user_num': u'首页抽奖点击用户数',
    'lottery_user_num1': u'热量页抽奖点击用户数',
    'lottery_user_num_total': u'抽奖点击总用户数',
    'black_card_num_total': u'首页黑卡点击次数',
    'black_card_num_total1': u'热量页黑卡点击次数',
    'black_card_user_num': u'首页黑卡点击用户数',
    'black_card_user_num1': u'热量页黑卡点击用户数',
    'black_card_user_num_total': u'黑卡点击用户总数',
    'free_envelope_num_total': u'首页淘宝红包点击次数',
    'free_envelope_num_total1': u'热量页淘宝红包点击次数',
    'free_envelope_user_num': u'首页淘宝红包点击用户数',
    'free_envelope_user_num1': u'热量页淘宝红包点击用户数',
    'free_envelope_user_num_total': u'淘宝红包点击总用户数',
    'hungry_num_total': u'日期',
    'hungry_num_total1': u'日期',
    'hungry_user_num': u'日期',
    'hungry_user_num1': u'日期',
    'hungry_user_num_total': u'日期',
    'million_experience_num_total': u'日期',
    'million_experience_num_total1': u'日期',
    'million_experience_user_num': u'日期',
    'million_experience_user_num1': u'日期',
    'million_experience_user_num_total': u'日期',
    'game_num_total': u'日期',
    'game_num_total1': u'日期',
    'game_user_num': u'日期',
    'game_user_num1': u'日期',
    'game_user_num_total': u'日期',
    'taobao_num_total': u'日期',
    'taobao_num_total1': u'日期',
    'taobao_user_num': u'日期',
    'taobao_user_num1': u'日期',
    'taobao_user_num_total': u'日期',
    'news_num_total': u'日期',
    'news_num_total1': u'日期',
    'news_user_num': u'日期',
    'news_user_num1': u'日期',
    'news_user_num_total': u'日期',
    'novels_num_total': u'日期',
    'novels_num_total1': u'日期',
    'novels_user_num': u'日期',
    'novels_user_num1': u'日期',
    'novels_user_num_total': u'日期',
    'play_num_total': u'日期',
    'play_num_total1': u'日期',
    'play_user_num': u'日期',
    'play_user_num1': u'日期',
    'play_user_num_total': u'日期',
    'video_num_total': u'补抢红包点击视频次数',
    'video_num_total1': u'抢红包翻倍点击视频次数',
    'video_num_total2': u'步数兑换翻倍点击视频次数',
    'video_num_total3': u'签到翻倍点击视频次数',
    'video_num_total4': u'看视频点击视频次数',
    'video_user_num': u'补抢红包',
    'video_user_num1': u'日期',
    'video_user_num2': u'日期',
    'video_user_num3': u'日期',
    'video_user_num4': u'日期',
    'video_user_num_total': u'日期',
    'banner_num_total': u'补抢红包展示banner次数',
    'banner_num_total1': u'抢红包展示banner次数',
    'banner_num_total2': u'步数兑换展示banner次数',
    'banner_num_total3': u'签到展示banner次数',
    'banner_user_num': u'日期',
    'banner_user_num1': u'日期',
    'banner_user_num2': u'日期',
    'banner_user_num3': u'日期',
    'banner_user_num_total': u'日期'
}

if __name__ == '__main__':
    statistical_day_cur = statistical_day.find()
    for statistical_day_obj in statistical_day_cur:
        print (statistical_day_obj.get('today_str'), statistical_day_obj.get('red_average_num'), statistical_day_obj.get(
            'user_red_record'), statistical_day_obj.get('user_num'), statistical_day_obj.get('user_num_active'))