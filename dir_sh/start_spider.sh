#!/bin/bash
ROOT_PATH=`dirname $0`
cd $ROOT_PATH
cd ..
ps -ef|grep spider_client.py|grep -v grep|awk '{print $2}'|xargs kill -9
python spider_client.py &