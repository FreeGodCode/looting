# -*- coding: utf8 -*-

import base64
import hashlib
import random
import string
import time
import zlib
from binascii import (b2a_hex, a2b_hex)

from Crypto.Cipher import AES


class XKcrypt():
    def __init__(self, key='szsyqfkjyxgs'):
        """
        小葵加密解密类
        :param key:加密解密密钥
        """
        self.key = hashlib.new("md5", key).digest()
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        """
        对字符串加密，如果text不是16的倍数（加密文本text必须为16的倍数！），会自动补足为16的倍数
        :param text: 要加密的字符串
        :return: 加密后的字符串
        """
        cryptor = AES.new(self.key, self.mode,
                          self.key)  # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        text_len = 16
        count = len(text)
        add = text_len - (count % text_len)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        """
        解密加密字符串，解密后去掉补足的空格
        :param text:加密过的字符串
        :return:解密后的字符串
        """
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')


class Sign:
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        print(string)
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret


def encryption_zip(content):
    zip_db = XKcrypt('zip_db')
    gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
    zip_data = gzip_compress.compress(content) + gzip_compress.flush()
    e_str = zip_db.encrypt(base64.b64encode(zip_data))
    return e_str


def decrypt_zip(content):
    zip_db = XKcrypt('zip_db')
    g_str = zip_db.decrypt(content)
    gzip_str = base64.b64decode(g_str)
    d_str = zlib.decompress(gzip_str, 16 + zlib.MAX_WBITS)
    return d_str


if __name__ == '__main__':
    print(encryption_zip('pc001762仕多副食店'))
    print(decrypt_zip(encryption_zip('pc001762仕多副食店')))

    pc = XKcrypt()  # 初始化密钥
    e = pc.encrypt("pc001762仕多副食店")  # 加密
    d = pc.decrypt(e)  # 解密
    print(e, d)
