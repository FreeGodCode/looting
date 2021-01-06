# -*- coding:utf-8 -*-

import os
import socket

'''
    监控端口服务是否down掉  down了就自动重启服务
'''


def monitor_port(port, serv_name):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect(('127.0.0.1', port))
        print('Server port {0} OK!'.format(port))
    except Exception:
        os.system('service {0} start'.format(serv_name))
    sk.close()


def monitor_gunicorn():
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect(('127.0.0.1', 8081))
        print('Server port 8080 OK!')
    except Exception as  e:
        print(str(e))
        os.system('sudo sh /root/planet_back/dir_sh/restartgun.sh')
    sk.close()


if __name__ == '__main__':
    # monitor_port(27889, 'mongod')
    monitor_port(80, 'nginx')
    monitor_gunicorn()
