# -*- coding: utf8 -*-
import copy

from pymongo.errors import DuplicateKeyError

from libs.db import operation

default_des = {
    'task1_cash': u'完成新手任务第一步奖励现金(单位分)',
    'task2_cash': u'完成新手任务第二步奖励现金(单位分)',
    'bind_phone_cash': u'绑定手机奖励现金(单位分)',
    'bind_invite_cash': u'绑定邀请码奖励现金(单位分)',

    'effective_invitation_num': u'有效邀请多少人成为球主',
    'calorific_number_people': u'一天有效邀请奖励现金与热量的最高人数',
    'effective_invitation_calorific': u'有效邀请完成提现奖励热量值',
    'effective_invitation_cash1': u'有效邀请直接奖励现金值(单位分)',
    'effective_invitation_cash2': u'有效邀请完成提现奖励现金值(单位分)',
    'commission_percent_1': u'球主享原住居民红包收益百分比',
    'commission_percent_2': u'球主享附属居民红包收益百分比',

    'red_failure_time': u'多少分钟内未抢红包只能补抢',
    'makeup_red_times': u'一天补抢最高次数',
    'makeup_red_cash': u'补抢红包最高金额(单位分)',
    'makeup_red_cash_lowest': u'补抢红包最低金额(单位分)',
    'makeup_red_day': u'用户新进前几天按下方设置补抢方式',
    'makeup_red_condition': u'补抢方式',

    'red_lowest_calorific': u'热量值低于多少无法抢红包',
    'red_returnp_calorific': u'正常抢红包后所返热量值',
    'returnp_calorific_double_times': u'一天正常抢红包返热量值翻倍最高次数',
    'red_double_cash': u'正常抢红包值小于等于多少红包翻倍(单位分)',
    'red_double_day': u'用户新进前几天按下方设置翻倍方式',
    'red_double_condition': u'翻倍方式',

    'penny_calorific': u'多少热量价值一分钱',
    'dividend_of_calorific': u'可用热量低于多少不参与分红',
    'dividend_deduct_calorific_per': u'参与分红时扣除当前可用热量的百分比',

    'transfer_activity_title': u'微转活动标题',
    'transfer_activity_time': u'微转活动时间',
    'wechat_transfer_cash': u'一个有效阅读奖励的现金值(单位分)',
    'wechat_transfer_calorific': u'一个有效阅读奖励的热量值',
    'wechat_transfer_per_deduction': u'微转文章扣量百分比',
    'wechat_trsf_display_quantity': u'微信转发在热量首页显示的数据条数',
    'step_count_calorific': u'多少步数兑换一热量',
    'step_count_day': u'一天最多兑换步数',
    'watch_video_calorific': u'观看视频奖励的热量值',
    'watch_video_times': u'一天最多观看视频奖励热量次数',
    'read_ad_calorific': u'浏览一次广告获得的热量',
    'novice_task_calorific': u'完成新手任务奖励热量',
    'name_verified_calorific': u'实名认证奖励热量',
    'bind_alipay_calorific': u'绑定支付宝奖励热量',
    'bind_wechat_calorific': u'绑定微信奖励热量',
    'share_reward_calorific': u'分享一次获得的热量',

    'integer_red_failure_time': u'整点红包失效时长(单位分钟)',
    'integer_red_consume_calorific': u'参与一次整点红包消耗的热量值',
    'integer_red_calorific_num': u'整点红包被抢完了通过看视频获取热量的最高次数',
    'integer_red_calorific': u'整点红包被抢完了通过看视频获取到的热量值',
    'integer_red_calorific_return_num': u'整点红包参与但未抢到通过看视频反返热量的最高次数',
    'integer_red_return_calorific': u'整点红包参与但未抢到通过看视频反返的热量值',
    'integer_red_number': u'整点红包点总资金百分之 1 时发的红包个数',

    'guess_red_consume_calorific': u'第一次参与猜红包消耗的热量值',
    'guess_red_consume_calorific_maximum': u'猜红包消耗翻倍耗递增消耗热量的最大值',
    'guess_red_num_prompt': u'猜红包参与几次之后才能通过看视频看最后一个数字的提示',
    'guess_red_invalid_time': u'猜红包失效时长(分钟)',
    'red_hour_per_json': u'红包时间点分配比例json数据',

    'automatic_withdraw_cash': u'提现金额少于多少自动提现',
    'new_withdraw_cash': u'新人提现体验金',
    'withdraw_cash_json': u'提现json数据',
    'withdraw_cash_json_new': u'新的提现json数据',
    'check_in_calorific_json': u'每日签到奖热量json数据',
    'calorific_cash_json': u'累计热量解锁红包json数据'
}

default_values = {
    'task1_cash': 0,
    'task2_cash': 0,
    'bind_phone_cash': 0,
    'bind_invite_cash': 0,
    'penny_calorific': 0,
    'effective_invitation_num': 0,
    'calorific_number_people': 0,
    'effective_invitation_calorific': 0,
    'effective_invitation_cash1': 0,
    'effective_invitation_cash2': 0,
    'step_count_calorific': 0,
    'step_count_day': 0,
    'commission_percent_1': 0,
    'commission_percent_2': 0,
    'red_failure_time': 0,
    'makeup_red_times': 0,
    'makeup_red_cash': 0,
    'makeup_red_cash_lowest': 0,
    'makeup_red_day': 0,
    'makeup_red_condition': 0,
    'red_lowest_calorific': 0,
    'red_returnp_calorific': 0,
    'returnp_calorific_double_times': 0,
    'red_double_cash': 0,
    'red_double_day': 0,
    'red_double_condition': 0,
    'read_ad_calorific': 0,
    'novice_task_calorific': 0,
    'name_verified_calorific': 0,
    'bind_alipay_calorific': 0,
    'bind_wechat_calorific': 0,
    'share_reward_calorific': 0,
    'watch_video_calorific': 0,
    'watch_video_times': 0,

    'dividend_of_calorific': 0,
    'dividend_deduct_calorific_per': 0,
    'transfer_activity_title': u'',
    'transfer_activity_time': u'',
    'wechat_transfer_cash': 0,
    'wechat_transfer_calorific': 0,
    'wechat_trsf_display_quantity': 0,
    'wechat_transfer_per_deduction': 0,

    'integer_red_failure_time': 0,
    'integer_red_consume_calorific': 0,
    'integer_red_calorific_num': 0,
    'integer_red_calorific': 0,
    'integer_red_calorific_return_num': 0,
    'integer_red_return_calorific': 0,
    'integer_red_number': 0,

    'guess_red_consume_calorific': 0,
    'guess_red_consume_calorific_maximum': 0,
    'guess_red_invalid_time': 5,
    'guess_red_num_prompt': 0,
    'red_hour_per_json': '{}',

    'automatic_withdraw_cash': 0,
    'new_withdraw_cash': 0,
    'withdraw_cash_json': '[]',
    'withdraw_cash_json_new': '[]',
    'check_in_calorific_json': '[]',
    'calorific_cash_json': '[]'
}
makeup_red_condition_values = {
    0: u'分享补抢',
    1: u'看视频补抢',
    2: u'分享或看视频补抢'
}
red_double_condition_values = {
    0: u'分享翻倍',
    1: u'看视频翻倍',
    2: u'分享或看视频翻倍'
}

int_key = ['task1_cash', 'task2_cash', 'bind_phone_cash', 'bind_invite_cash', 'penny_calorific',
           'effective_invitation_num', 'effective_invitation_calorific', 'effective_invitation_cash1',
           'effective_invitation_cash2', 'step_count_calorific', 'step_count_day', 'commission_percent_1',
           'commission_percent_2', 'red_failure_time', 'makeup_red_times', 'makeup_red_cash', 'red_lowest_calorific',
           'red_returnp_calorific', 'new_withdraw_cash', 'returnp_calorific_double_times', 'read_ad_calorific',
           'makeup_red_cash_lowest', 'makeup_red_day', 'makeup_red_condition', 'red_double_cash', 'red_double_day',
           'red_double_condition', 'novice_task_calorific', 'name_verified_calorific', 'bind_alipay_calorific',
           'bind_wechat_calorific', 'share_reward_calorific', 'calorific_number_people', 'automatic_withdraw_cash',
           'watch_video_calorific', 'watch_video_times', 'dividend_of_calorific', 'dividend_deduct_calorific_per',
           'wechat_transfer_cash', 'wechat_transfer_calorific', 'integer_red_consume_calorific',
           'integer_red_calorific_num', 'integer_red_calorific', 'integer_red_calorific_return_num',
           'integer_red_return_calorific', 'integer_red_number', 'guess_red_consume_calorific',
           'guess_red_consume_calorific_maximum', 'guess_red_num_prompt', 'wechat_trsf_display_quantity',
           'wechat_transfer_per_deduction', 'guess_red_invalid_time', 'integer_red_failure_time']

float_key = []


def _insert(data):
    global default_values
    add_dict = copy.copy(default_values)
    for key in default_values:
        if key in data:
            _values = data.get(key)
            # if isinstance(_values, str) or isinstance(_values, unicode):
            if isinstance(_values, str):
                _values = _values.strip()
            if key in int_key:
                try:
                    _values = int(_values)
                except:
                    return {'status': False, 'msg': u'参数错误'}
            if key in float_key:
                try:
                    _values = float(_values)
                except:
                    return {'status': False, 'msg': u'参数错误'}
            add_dict.update({key: _values})
    try:
        operation.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True}


if __name__ == '__main__':
    _insert({})
