# -*- coding: utf8 -*-
import os
import traceback
from datetime import timedelta

from flask import jsonify

from apps.admin.api import admin_api_blue
from apps.admin.views import admin_blue
from apps.advert.api import advert_api_blue
from apps.advert.views import advert_blue
from apps.carousel.api import carousel_api_blue
from apps.carousel.views import carousel_blue
from apps.common.api import common_api_blue
from apps.configs.daily_attendance_config.api import daily_attendance_config_api_blue
from apps.configs.daily_attendance_config.views import daily_attendance_config_blue
from apps.configs.daily_new_config.api import daily_new_config_api_blue
from apps.configs.daily_new_config.views import daily_new_config_blue
from apps.configs.dividend_config.api import dividend_config_api_blue
from apps.configs.dividend_config.views import dividend_config_blue
from apps.configs.invite_reward_config.api import invite_reward_config_api_blue
from apps.configs.invite_reward_config.views import invite_reward_config_blue
from apps.configs.invite_task_config.api import invite_task_config_api_blue
from apps.configs.invite_task_config.views import invite_task_config_blue
from apps.configs.new_user_config.api import new_user_config_api_blue
from apps.configs.new_user_config.views import new_user_config_blue
from apps.configs.route_config.api import route_config_api_blue
from apps.configs.route_config.views import route_config_blue
from apps.configs.user_level_config.api import user_level_config_api_blue
from apps.configs.user_level_config.views import user_level_config_blue
from apps.configs.withdraw_config.api import withdraw_config_api_blue
from apps.configs.withdraw_config.views import withdraw_config_blue
from apps.daily_new.api import daily_new_api_blue
from apps.daily_new.views import daily_new_blue
from apps.daily_task.api import daily_task_api_blue
from apps.daily_task.views import daily_task_blue
from apps.domain_h5.api import domain_h5_api_blue
from apps.domain_h5.views import domain_h5_blue
from apps.flash_sale.api import flash_sale_api_blue
from apps.flash_sale.views import flash_sale_blue
from apps.login.views import login_blue
from apps.order.api import order_api_blue
from apps.order.views import order_blue
from apps.product.api import product_api_blue
from apps.product.views import product_blue
from apps.role.api import role_api_blue
from apps.role.views import role_blue
from apps.system.api import system_api_blue
from apps.system.views import system_blue
from apps.operation.views import operation_blue
from apps.operation.api import operation_api_blue
from apps.task_event.api import task_event_api_blue
from apps.task_event.views import task_event_blue
from apps.user.api import user_api_blue
from apps.user.views import user_blue
from apps.version_manag.api import version_manag_api_blue
from apps.version_manag.views import version_manag_blue
from apps.withdraw.api import withdraw_api_blue
from apps.withdraw.views import withdraw_blue
from conf import conf
from libs.exception_ex import ProcessError
from libs.flask_ex import FlaskEx, InternalProcessError

app = FlaskEx(__name__, static_folder='statices')

app.register_blueprint(login_blue)
app.register_blueprint(common_api_blue)

app.register_blueprint(system_blue)
app.register_blueprint(system_api_blue)

app.register_blueprint(operation_blue)
app.register_blueprint(operation_api_blue)

app.register_blueprint(admin_blue)
app.register_blueprint(admin_api_blue)

app.register_blueprint(role_blue)
app.register_blueprint(role_api_blue)

app.register_blueprint(user_api_blue)
app.register_blueprint(user_blue)

app.register_blueprint(domain_h5_api_blue)
app.register_blueprint(domain_h5_blue)
app.register_blueprint(version_manag_blue)
app.register_blueprint(version_manag_api_blue)

app.register_blueprint(product_blue)
app.register_blueprint(product_api_blue)
app.register_blueprint(daily_new_blue)
app.register_blueprint(daily_new_api_blue)
app.register_blueprint(flash_sale_blue)
app.register_blueprint(flash_sale_api_blue)
app.register_blueprint(order_blue)
app.register_blueprint(order_api_blue)
app.register_blueprint(daily_task_blue)
app.register_blueprint(daily_task_api_blue)
app.register_blueprint(withdraw_blue)
app.register_blueprint(withdraw_api_blue)
app.register_blueprint(task_event_blue)
app.register_blueprint(task_event_api_blue)
app.register_blueprint(daily_new_config_blue)
app.register_blueprint(daily_new_config_api_blue)

# 复合配置蓝图
app.register_blueprint(daily_attendance_config_blue)
app.register_blueprint(daily_attendance_config_api_blue)
app.register_blueprint(dividend_config_blue)
app.register_blueprint(dividend_config_api_blue)
app.register_blueprint(invite_reward_config_blue)
app.register_blueprint(invite_reward_config_api_blue)
app.register_blueprint(route_config_blue)
app.register_blueprint(route_config_api_blue)
app.register_blueprint(new_user_config_blue)
app.register_blueprint(new_user_config_api_blue)
app.register_blueprint(withdraw_config_blue)
app.register_blueprint(withdraw_config_api_blue)
app.register_blueprint(user_level_config_blue)
app.register_blueprint(user_level_config_api_blue)
app.register_blueprint(invite_task_config_blue)
app.register_blueprint(invite_task_config_api_blue)
app.register_blueprint(advert_blue)
app.register_blueprint(advert_api_blue)

app.register_blueprint(carousel_blue)
app.register_blueprint(carousel_api_blue)

app.config.update(SECRET_KEY=os.urandom(24))
app.permanent_session_lifetime = timedelta(minutes=24 * 60)


@app.errorhandler(InternalProcessError)
def internal_process_error(err):
    return jsonify({'code': err.get_code(), 'msg': err.get_msg()})


@app.errorhandler(ProcessError)
def process_error(error):
    return error


@app.errorhandler(404)
def internal_error(error):
    return '404', 404


@app.errorhandler(Exception)
def internal_error(e):
    traceback.print_exc()
    return '500', 500


# 自定义模板过滤器
@app.template_filter()
def strToUnicode(str):
    """
    字符串转unicode编码
    :param str: 要转换的字符串
    :return: 如果Unicode编码大于217返回&#8220;格式，否则原样返回
    """
    _str = u''
    for sn in str:
        c = ord(sn)
        if c > 217:
            _str += u'&#{0};'.format(c)
        else:
            _str += sn
    return _str


@app.template_filter()
def clearHtmlFormat(html):
    """
    清除html格式，2个以上的空格，换行符，回车，tab符号
    :param html: 要处理的html代码
    :return: 处理后的html字符串
    """
    return html.replace('  ', '').replace('	', '').replace('space', '').replace('\r\n', '').replace('\n', '')


if __name__ == '__main__':
    app.run(debug=conf.DEBUG, port=conf.PORT, host=conf.HOST)
