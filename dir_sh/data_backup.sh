#!/bin/bash
yes | rm -rf /root/mongo_data/planet_db
yes | mongodump -h 172.19.56.201:31962 -uyqf_planet -pplanet_0830_official --authenticationDatabase admin -d planet_db -o /root/mongo_data
month=`date +%m`
date_day=`date +%d`
hour=`date +%H`
myPath="/root/mongo_data/mongo_tar_$month/"
echo $myPath
if [ ! -d "$myPath" ]; then
        mkdir "$myPath"
fi
tar_file="/root/mongo_data/mongo_tar_$month/mongo_${date_day}_$hour.tar"
echo $tar_file
tar czvf $tar_file /root/mongo_data/planet_db