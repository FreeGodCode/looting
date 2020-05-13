#!/bin/bash
ROOT_PATH=`dirname $0`
cd $ROOT_PATH
cd ..
ps -ef|grep day.py|grep -v grep|awk '{print $2}'|xargs kill -9
python day.py &