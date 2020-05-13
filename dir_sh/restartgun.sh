#!/bin/bash
ROOT_PATH=`dirname $0`
cd $ROOT_PATH
cd ..
ps -ef|grep gun.py|grep -v grep|awk '{print $2}'|xargs kill -9
gunicorn -c gun.py run:app -D