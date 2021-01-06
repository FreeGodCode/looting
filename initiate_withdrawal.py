# -*- coding: utf-8 -*-

import json
import sys
import time
from datetime import datetime

from libs.common import withdraw_way
from libs.db import operation, withdraw_task_code, error_log


# reload(sys)
# sys.setdefaultencoding('utf-8')


def initiate_withdrawal():
    """
    自动 提现 线程
    :return:
    """
    hour_str = datetime.now().strftime(format='%H')
    operation_obj = operation.find_one()
    automatic_withdraw_cash = operation_obj.get('automatic_withdraw_cash')

    while True:
        withdraw_task = withdraw_task_code.brpop('withdraw_notice', timeout=1)
        if not withdraw_task:
            new_hour_str = datetime.now().strftime(format='%H')
            if new_hour_str != hour_str:
                break
            continue
        try:
            withdraw_json = json.loads(withdraw_task[1])
            serial_number = withdraw_json.get('serial_number')
            withdraw_way(serial_number, automatic_withdraw_cash, is_back=False)
        except Exception as e:
            error_log.insert_one({'req_url': '', 'req_data': '', 'req_method': 'initiate_withdrawal',
                                  'error_str': str(e), 'today': datetime.now().strftime(format='%Y-%m-%d'),
                                  'time_stamp': int(time.time()),
                                  'req_time': datetime.now().strftime(format='%Y-%m-%d %H:%M:%S')})

        new_hour_str = datetime.now().strftime(format='%H')
        if new_hour_str != hour_str:
            break


# 每小时执行一次的脚本
if __name__ == '__main__':
    try:
        # 自动 提现
        initiate_withdrawal()
    except:
        pass
