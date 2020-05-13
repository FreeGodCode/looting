# -*- coding: utf8 -*-
import multiprocessing

bind = "127.0.0.1:8081"  # 绑定IP和端口
workers = multiprocessing.cpu_count() + 1  # 最优进程数
backlog = 2048  # 等待连接最大数量
worker_class = 'gevent'  # 异步处理模块
worker_connections = 1000  # 单个worker最大链接数量
threads = multiprocessing.cpu_count() * 2 + 1  # 最优线程数
max_requests = 2000  # 单个worker最大请求数，超过这个数量worker会重启
pidfile = 'gun.pid'  # gunicorn进程ID
proc_name = 'server'  # gunicorn进程名，多个gunicorn实例时有用，要安装setproctitle
timeout = 30  # 连接超时时间
debug = True  # debug模式
loglevel = 'info'  # 日志级别
errorlog = 'log/error.log'  # 错误日志文件路径
# accesslog = 'log/access.log'  # 正常日志文件路径

reload=True
