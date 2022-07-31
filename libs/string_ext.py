# -*- coding: utf8 -*-
# author: ty


def ensure_start_with(original, string):
    """
    确保字符串头部的字符为 string
    :param original:
    :param string:
    :return:
    """
    try:
        return original if original.startswith(string) else string + original
    except:
        return ''


def not_ensure_start_with(original, string):
    """
    确保字符串头部的字符 不为 string
    :param original:
    :param string:
    :return:
    """
    try:
        return original if not original.startswith(string) else original[1:]
    except:
        return ''


def ensure_end_with(original, string):
    """
    确保字符串尾部的字符为 string
    :param original:
    :param string:
    :return:
    """
    try:
        return original if original.endswith(string) else original + string
    except:
        return ''


def not_ensure_end_with(original, string):
    """
    确保字符串尾部的字符 不为 string
    :param original:
    :param string:
    :return:
    """
    try:
        return original if not original.endswith(string) else original[0:-1]
    except:
        return ''
