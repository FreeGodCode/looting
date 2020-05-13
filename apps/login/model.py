# -*- coding: utf8 -*-


admin_navs = [
    {
        "title": "首页",
        "icon": "layui-icon-home",
        "href": "/yqfadmin/index",
        "spread": True
    },
    {
        "title": "系统管理",
        "icon": "layui-icon-set",
        "spread": False,
        "children": [
            {
                "title": "系统配置",
                'name': 'system',
                "href": "system/edit",
                'authority_list': [{'title': '修改', 'value': 'system:edit'},
                                   {'title': '查看', 'value': 'system:get'},
                                   {'title': '上传', 'value': 'common:upload'}]
            }, 
            # {
            #     "title": "运营配置",
            #     'name': 'operation',
            #     "href": "operation/edit",
            #     'authority_list': [{'title': '修改', 'value': 'operation:edit'},
            #                        {'title': '查看', 'value': 'operation:get'}]
            # }, 
            {
                "title": "管理员",
                'name': 'admin',
                "href": "admin/list",
                'authority_list': [{'title': '增加', 'value': 'admin:create'},
                                   {'title': '删除', 'value': 'admin:delete'},
                                   {'title': '修改', 'value': 'admin:edit'},
                                   {'title': '查看', 'value': 'admin:get'},
                                   {'title': '设置角色', 'value': 'admin:role_set'}]
            }, {
                "title": "后台角色",
                'name': 'role',
                "href": "role/list",
                'authority_list': [{'title': '增加', 'value': 'role:create'},
                                   {'title': '删除', 'value': 'role:delete'},
                                   {'title': '修改', 'value': 'role:edit'},
                                   {'title': '查看', 'value': 'role:get'},
                                   {'title': '分配权限', 'value': 'role:permissions_allow'}]
            }, {
                "title": "版本管理",
                'name': 'version_manag',
                "href": "version_manag/list",
                'authority_list': [{'title': '增加', 'value': 'version:create'},
                                   {'title': '删除', 'value': 'version:delete'},
                                   {'title': '修改', 'value': 'version:edit'},
                                   {'title': '查看', 'value': 'version:get'}]
            }
        ]
    },
    {
        "title": "商城管理",
        "icon": "layui-icon-user",
        "spread": False,
        "children": [
            {
                "title": "商品列表",
                'name': 'product',
                "href": "product/list",
                'authority_list': [
                    {'title': '新增', 'value': 'product:add'},
                    {'title': '删除', 'value': 'product:delete'},
                    {'title': '修改', 'value': 'product:edit'},
                    {'title': '查看', 'value': 'product:get'}
                ]
            },
            {
                "title": "订单列表",
                'name': 'order',
                "href": "order/list",
                'authority_list': [
                    {'title': '修改', 'value': 'order:edit'},
                    {'title': '查看', 'value': 'order:get'}
                ]
            }
        ]
    },

    {
        "title": "配置中心",
        "icon": "layui-icon-user",
        "spread": False,
        "children": [
            {
                "title": "新用户配置",
                'name': 'new_user_config',
                "href": "new_user_config/edit",
                'authority_list': [
                    {'title': '修改', 'value': 'new_user_config:edit'},
                    {'title': '查看', 'value': 'new_user_config:get'}
                ]
            },
            {
                "title": "提现配置",
                'name': 'withdraw_config',
                "href": "withdraw_config/list",
                'authority_list': [
                    {'title': '新增', 'value': 'withdraw_config:add'},
                    {'title': '删除', 'value': 'withdraw_config:delete'},
                    {'title': '修改', 'value': 'withdraw_config:edit'},
                    {'title': '查看', 'value': 'withdraw_config:get'}
                ]
            },
            {
                "title": "用户等级配置",
                'name': 'user_level_config',
                "href": "user_level_config/list",
                'authority_list': [
                    {'title': '新增', 'value': 'user_level_config:add'},
                    {'title': '删除', 'value': 'user_level_config:delete'},
                    {'title': '修改', 'value': 'user_level_config:edit'},
                    {'title': '查看', 'value': 'user_level_config:get'}
                ]
            },
            {
                "title": "APP路由配置",
                'name': 'route_config',
                "href": "route_config/list",
                'authority_list': [
                    {'title': '新增', 'value': 'route_config:add'},
                    {'title': '删除', 'value': 'route_config:delete'},
                    {'title': '修改', 'value': 'route_config:edit'},
                    {'title': '查看', 'value': 'route_config:get'}
                ]
            },
            {
                "title": "邀请奖励配置",
                'name': 'invite_reward_config',
                "href": "invite_reward_config/list",
                'authority_list': [
                    {'title': '新增', 'value': 'invite_reward_config:add'},
                    {'title': '删除', 'value': 'invite_reward_config:delete'},
                    {'title': '修改', 'value': 'invite_reward_config:edit'},
                    {'title': '查看', 'value': 'invite_reward_config:get'}
                ]
            },
            {
                "title": "邀请奖励任务配置",
                'name': 'invite_task_config',
                "href": "invite_task_config/edit",
                'authority_list': [
                    {'title': '修改', 'value': 'invite_task_config:edit'},
                    {'title': '查看', 'value': 'invite_task_config:get'}
                ]
            },
            {
                "title": "分红配置",
                'name': 'dividend_config',
                "href": "dividend_config/list",
                'authority_list': [
                    {'title': '新增', 'value': 'dividend_config:add'},
                    {'title': '删除', 'value': 'dividend_config:delete'},
                    {'title': '修改', 'value': 'dividend_config:edit'},
                    {'title': '查看', 'value': 'dividend_config:get'}
                ]
            },
            {
                "title": "每日签到配置",
                'name': 'daily_attendance_config',
                "href": "daily_attendance_config/list",
                'authority_list': [
                    {'title': '新增', 'value': 'daily_attendance:add'},
                    {'title': '删除', 'value': 'daily_attendance:delete'},
                    {'title': '修改', 'value': 'daily_attendance:edit'},
                    {'title': '查看', 'value': 'daily_attendance:get'}
                ]
            },
            {
                "title": "每日任务配置",
                'name': 'daily_task',
                "href": "daily_task/list",
                'authority_list': [
                    {'title': '新增', 'value': 'daily_task:add'},
                    {'title': '删除', 'value': 'daily_task:delete'},
                    {'title': '修改', 'value': 'daily_task:edit'},
                    {'title': '查看', 'value': 'daily_task:get'}
                ]
            },
        ]
    },
    {
        "title": "运营管理",
        "icon": "layui-icon-user",
        "spread": False,
        "children": [
            {
                "title": "提现管理",
                'name': 'withdraw',
                "href": "withdraw/list",
                'authority_list': [
                    {'title': '审核微信首次提现', 'value': 'withdraw:wechat_pay'},
                    {'title': '审核支付宝提现', 'value': 'withdraw:alipay'},
                    {'title': '修改', 'value': 'withdraw:edit'},
                    {'title': '查看', 'value': 'withdraw:get'}
                ]
            },
            # {
            #     "title": "用户列表",
            #     'name': 'user',
            #     "href": "user/list",
            #     'authority_list': [
            #         {'title': '新增', 'value': 'user:add'},
            #         {'title': '删除', 'value': 'user:delete'},
            #         {'title': '修改', 'value': 'user:edit'},
            #         {'title': '查看', 'value': 'user:get'}
            #     ]
            # },
        ]
    },
    {"title": "每日上新",
     "icon": "layui-icon-user",
     "spread": False,
     "children": [
         {
             "title": "规则设置",
             'name': 'daily_new',
             "href": "daily_new_config/list",
             'authority_list': [
                 {'title': '新增', 'value': 'daily_new_config:add'},
                 {'title': '删除', 'value': 'daily_new_config:delete'},
                 {'title': '修改', 'value': 'daily_new_config:edit'},
                 {'title': '查看', 'value': 'daily_new_config:get'}
             ]
         },
         {
             "title": "上新列表",
             'name': 'daily_new',
             "href": "daily_new/list",
             'authority_list': [
                 {'title': '新增', 'value': 'daily_new:add'},
                 {'title': '删除', 'value': 'daily_new:delete'},
                 {'title': '修改', 'value': 'daily_new:edit'},
                 {'title': '查看', 'value': 'daily_new:get'}
             ]
         },
         {
             "title": "上新实时列表",
             'name': 'daily_new',
             "href": "daily_new/real_list",
             'authority_list': [
                 {'title': '查看', 'value': 'daily_new:get'}
             ]
         },
     ]
     },
    {"title": "秒杀",
     "icon": "layui-icon-user",
     "spread": False,
     "children": [
         {
             "title": "时间规则",
             'name': 'flash_sale',
             "href": "flash_sale/config",
             'authority_list': [
                 {'title': '修改', 'value': 'flash_sale:edit'},
                 {'title': '查看', 'value': 'flash_sale:get'}
             ]
         },
         {
             "title": "秒杀列表",
             'name': 'flash_sale',
             "href": "flash_sale/list",
             'authority_list': [
                 {'title': '新增', 'value': 'flash_sale:add'},
                 {'title': '删除', 'value': 'flash_sale:delete'},
                 {'title': '修改', 'value': 'flash_sale:edit'},
                 {'title': '查看', 'value': 'flash_sale:get'}
             ]
         },
         {
             "title": "秒杀实时列表",
             'name': 'flash_sale',
             "href": "flash_sale/real_list",
             'authority_list': [
                 {'title': '查看', 'value': 'flash_sale:get'}
             ]
         },
     ]
     },
    {
        "title": "用户管理",
        "icon": "layui-icon-user",
        "spread": False,
        "children": [
            {
                "title": "用户列表",
                'name': 'user',
                "href": "user/list",
                'authority_list': [
                    {'title': '新增', 'value': 'user:add'},
                    {'title': '删除', 'value': 'user:delete'},
                    {'title': '修改', 'value': 'user:edit'},
                    {'title': '查看', 'value': 'user:get'}
                ]
            }, {
                "title": "提现管理",
                'name': 'withdraw',
                "href": "withdraw/list",
                'authority_list': [
                    {'title': '审核微信首次提现', 'value': 'withdraw:wxpay'},
                    {'title': '审核支付宝提现', 'value': 'withdraw:alipay'},
                    {'title': '修改', 'value': 'withdraw:edit'},
                    {'title': '查看', 'value': 'withdraw:get'}
                ]
            }, {
                "title": "意见反馈",
                "href": "feedback/list",
                'authority_list': [{'title': '修改', 'value': '1_2_2'}, {'title': '查看', 'value': '1_2_3'}]
            }, {
                "title": " 邀请总排行",
                "href": "leaderboard/list",
                'authority_list': [{'title': '查看', 'value': '1_3_3'}]
            }, {
                "title": "用户类型占比",
                "href": "statistical/user_analysis_list",
                'authority_list': [{'title': '查看', 'value': '1_4_3'}]
            }, {
                "title": "用户金额占比",
                "href": "statistical/user_balance_list",
                'authority_list': [{'title': '查看', 'value': '1_5_3'}]
            }, {
                "title": " 提现排行榜",
                "href": "leaderboard_withdraw/list",
                'authority_list': [{'title': '查看', 'value': '1_6_3'}]
            }
        ]
    },
    {
        "title": "素材管理",
        "icon": "layui-icon-table",
        "spread": False,
        "children": [
            {
                "title": "轮播列表",
                "href": "carousel/list",
                'authority_list': [{'title': '增加', 'value': 'carousel:add'},
                                   {'title': '删除', 'value': 'carousel:delete'},
                                   {'title': '修改', 'value': 'carousel:edit'},
                                   {'title': '查看', 'value': 'carousel:get'}]
            }
            , {
                "title": "文档管理",
                "href": "help_center/list",
                'authority_list': [{'title': '增加', 'value': 'help_center:add'},
                                   {'title': '删除', 'value': 'help_center:delete'},
                                   {'title': '修改', 'value': 'help_center:edit'},
                                   {'title': '查看', 'value': 'help_center:get'}]
            }, {
                "title": "推广域名",
                "href": "domain_h5/list",
                'authority_list': [{'title': '增加', 'value': 'domain_h5:add'},
                                   {'title': '删除', 'value': 'domain_h5:delete'},
                                   {'title': '修改', 'value': 'domain_h5:edit'},
                                   {'title': '查看', 'value': 'domain_h5:get'}]
            }, {
                "title": "广告库",
                "href": "advert/list",
                'authority_list': [{'title': '增加', 'value': 'advert:add'},
                                   {'title': '删除', 'value': 'advert:delete'},
                                   {'title': '修改', 'value': 'advert:edit'},
                                   {'title': '查看', 'value': 'advert:get'}]
            }]
    }, {
        "title": "数据统计",
        "icon": "layui-icon-chart",
        "spread": False,
        "children": [{
            "title": "星球统计",
            "href": "statistical/planet_data_chart",
            'authority_list': [{'title': '增加', 'value': '3_0_0'}, {'title': '删除', 'value': '3_0_1'},
                               {'title': '修改', 'value': '3_0_2'}, {'title': '查看', 'value': '3_0_3'}]
        }, {
            "title": "用户统计",
            "href": "statistical/user_data_chart",
            'authority_list': [{'title': '增加', 'value': '3_1_0'}, {'title': '删除', 'value': '3_1_1'},
                               {'title': '修改', 'value': '3_1_2'}, {'title': '查看', 'value': '3_1_3'}]
        }, {
            "title": "热量统计",
            "href": "statistical/heat_data_chart",
            'authority_list': [{'title': '增加', 'value': '3_2_0'}, {'title': '删除', 'value': '3_2_1'},
                               {'title': '修改', 'value': '3_2_2'}, {'title': '查看', 'value': '3_2_3'}]
        }, {
            "title": "现金统计",
            "href": "statistical/red_data_chart",
            'authority_list': [{'title': '增加', 'value': '3_3_0'}, {'title': '删除', 'value': '3_3_1'},
                               {'title': '修改', 'value': '3_3_2'}, {'title': '查看', 'value': '3_3_3'}]
        }, {
            "title": "用户留存与活跃",
            "href": "statistical/user_list",
            'authority_list': [{'title': '查看', 'value': '3_4_3'}]
        }, {
            "title": "渠道推广",
            "href": "statistical/statistical_official_invite",
            'authority_list': [{'title': '查看', 'value': '3_5_3'}]
        }]
    },
    {
        "title": "点击统计",
        "icon": "layui-icon-chart",
        "spread": False,
        "children": [{
            "title": "视频统计",
            "href": "statistical/video_list",
            'authority_list': [{'title': '查看', 'value': '4_0_3'}]
        }, {
            "title": "首页广告",
            "href": "statistical/home_ad_list",
            'authority_list': [{'title': '查看', 'value': '4_1_3'}]
        }]
    },
    {
        "title": "账户管理",
        "icon": "layui-icon-username",
        "spread": False,
        "children": [{
            "title": "修改密码",
            "icon": " fa-edit",
            "href": "yqfadmin/revise_psw"
        }, {
            "title": "登录日志",
            "icon": "fa-file-text-o",
            "href": "yqfadmin/login_log"
        }]
    },
]

base_navs = [
    {
        "title": "首页",
        "icon": "layui-icon-home",
        "href": "/yqfadmin/index",
        "spread": True
    },
    {
        "title": "系统管理",
        "icon": "layui-icon-set",
        "spread": False,
        "children": []
    },
    {
        "title": "商城管理",
        "icon": "layui-icon-user",
        "spread": False,
        "children": []
    },
    {
        "title": "配置中心",
        "icon": "layui-icon-user",
        "spread": False,
        "children": []
    },
    {
        "title": "运营管理",
        "icon": "layui-icon-user",
        "spread": False,
        "children": []
    },
    {
        "title": "每日上新",
        "icon": "layui-icon-user",
        "spread": False,
        "children": []
    },
    {
        "title": "秒杀",
        "icon": "layui-icon-user",
        "spread": False,
        "children": []
    },

    {
        "title": "用户管理",
        "icon": "layui-icon-user",
        "spread": False,
        "children": []
    },
    {
        "title": "素材管理",
        "icon": "layui-icon-template-1",
        "spread": False,
        "children": []
    },
    {
        "title": "统计数据",
        "icon": "layui-icon-chart",
        "spread": False,
        "children": []
    }, {
        "title": "点击统计",
        "icon": "layui-icon-chart",
        "spread": False,
        "children": []
    },
    {
        "title": "账户管理",
        "icon": "layui-icon-username",
        "spread": False,
        "children": [{
            "title": "修改密码",
            "icon": " fa-edit",
            "href": "yqfadmin/revise_psw"
        }, {
            "title": "登录日志",
            "icon": "fa-file-text-o",
            "href": "yqfadmin/login_log"
        }]
    },
]
