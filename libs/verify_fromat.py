# -*- coding: utf8 -*-
import re


def verify_mobile(mobile):
    match_phone = re.match('^1[3|4|5|6|7|8|9]\d{9}$', mobile)
    return match_phone is not None


def verify_mail(mail):
    match_mail = re.match('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', mail)
    return match_mail is not None
