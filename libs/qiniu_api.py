# -*- coding: utf8 -*-

from qiniu import (Auth, put_data)

from libs.db import redis_error


def qiniu_upload_file(fname, data, bucket_name, access_key, secret_key, qn_url):
    """
    把二维码图片保存到七牛空间
    :param fname:图片文件名
    :return:返回图片地址
    """
    # 获取token
    q = Auth(access_key, secret_key)
    token = q.upload_token(bucket_name, fname, 3600)
    number = 0
    ret = None
    while not ret:
        ret, err = put_data(token, fname, data)
        if not ret:
            redis_error.lpush('qiniu_error', str(err))
        number += 1
        if number >= 10:
            break
    try:
        url = qn_url + ret['key']
    except:
        url = ''
    return url

#
# def qiniu_delete_file(name):
#     bucket_name = CONF.bucket_name
#     access_key = CONF.access_key
#     secret_key = CONF.secret_key
#     # 初始化Auth状态
#     q = Auth(access_key, secret_key)
#     # 初始化BucketManager
#     bucket = BucketManager(q)
#     # 你要测试的空间， 并且这个key在你空间中存在
#     ret, info = bucket.delete(bucket_name, name)
#     print(info)
#     assert ret == {}
#
#
# def fetch(url, name=None):
#     """
#     将图片上传到七牛
#
#     :param url: 图片原地址
#     :param name: 图片文件名
#     :return:
#     """
#     url = url.split('?')[0]
#     print url
#     if not name:
#         raise ValueError(u'文件名不能为空')
#     # 初始化权限信息
#     bucket_name = CONF.bucket_name
#     access_key = CONF.access_key
#     secret_key = CONF.secret_key
#     # 获取token
#     q = Auth(access_key, secret_key)
#     pic_bucket = BucketManager(q)
#     ret, info = pic_bucket.fetch(
#         url=url,
#         bucket=bucket_name,
#         key=name)
#     try:
#         assert isinstance(ret, dict)
#     except:
#         return False
#     try:
#         url = CONF.QN_URL + ret['key']
#     except:
#         return False
#     return url
#
#
# def fetch_content_xiaokui(content):
#     """
#     把文章内的图片保存到七牛空间，并替换文章中的图片链接
#     :param content:文章内容
#     :return:返回处理后的内容
#     """
#     srcs = get_center_str_all('src="', '"', content)
#     for src in srcs:
#         if src.find('tuoluocaijing.cn') > -1:
#             continue
#         name = md5(src)
#         for i in range(3):
#             src_new = fetch(src, name)
#             if src_new:
#                 break
#         if src_new:
#             content = content.replace('src="' + src, 'src="' + src_new + '?imageView2/3/w/760/h/100/q/75|imageslim')
#     return content
#
#
# if __name__ == '__main__':
#     content = '<p style="color: rgb(51, 51, 51);"><img class="__bg_gif" data-ratio="0.66796875" data-type="gif" data-w="480" data-src="https://mmbiz.qpic.cn/mmbiz_gif/svgxOMD0rYMFVceLhsDJrnMNicfSQMHx2myN3IicWibjLgHfjrLPC1ToQRgibm7KpXAkRmRym8pV6wKdjgB2aDwEgg/640?wx_fmt=gif" style="visibility: visible !important;width:auto !important;max-width:100% !important;height:auto !important;"  /></p>'
#     url = fetch_content_xiaokui(content)
#     print url
