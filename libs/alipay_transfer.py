# -*- coding: utf-8 -*-
import sys

from alipay import AliPay

reload(sys)
sys.setdefaultencoding('utf-8')


class Payment():
    def __init__(self, appid, url):
        '''
        支付接口初始化
        :param appid: 商户appid
        :param url: 支付宝接口url
        '''
        self.app_private_key_string = '-----BEGIN PRIVATE KEY-----\nMIIEowIBAAKCAQEAqZMJzkFNcLzWQrgbXtZIDKNoWAIOv8P+TegdlGvjmabh+2lQTxJ+x3od7UgIBsJsdFzYCx1EADQu/q9nObBqMgNIYGY0yX0nDPiMnmh7VnL232y7dMGr/N0HSKSLEuHmF7J3eTMcom+I0WQ9KMIsdYpx9mOQnKZqpkfYj2J/Gv+ZGW6WRsGZZarDLAOpSJWTVrhnJsYczMbOtJi1T4yCnkauMbdH+n7+s5Q1c1WnMmxJSzBOyxCJTpUIcwG/yhM94g5bY853YTrmCxNQwkf6gmP3JNmK9yMVKsizS6ycgdAKrBALgo+TxhqtNBdvg2shHSdXRx2/mgiD0TFPeHWsDQIDAQABAoIBAQCFi+xUCG/RkpZ3MwEzPjS95088yFoPQm6bsmrhQdqcXqZoVndN3rYDqTO6dFkF4caCGcB3eFPeiTpdj4wPDdWEj7tHWBbIfAzuFSzBcG16Fs5ABSTYfdJSMUwUNKnmdAu+q+mVhOBPOOGaboQP/mP/Kco4jg8Mn68sRzbRLXQGsO0Es2u0iIemRUorHiGLl+HUbzDoz/J5gthuqismQxL+MpdLDGK59hVtf8IYTRGNovTN/nTQHp4HJSB0MSYQtAP0GOOkAoYxsY7b9N3/EM8HA2unF2lk/zsnsIMkT7VGXBLIR3U3kEmiCgEkryT2GqEF8xlpcM3p+f9nZf33sysNAoGBAOkgD0ELzu7HPNlv6tth6xf3ZuKe50BdCq/S41fvjm/Po8ya+YYX0hUDHX5w22S2noKI/2GnOsCEHpZS6f6/GazB+x/OxgVnO0FpkEE+tJrcgfgqCZo5QwaXl8f+1qAud2NdFxNUOneWHfEN5RSez0WipMufYCqAoCObTjjcpqlXAoGBALo2oEgw0EDO8X1OrZIrUzGj+DTWq662hvb2DSXIAJtUXp1KowEZS7mQiQyMpGubvRlF8Sqmo0kzhPxLU3dUBnRkOebyBGHJO7Nsi6qacTQradeGgpT8HC5iP1+WhvcSlkGEjyAxcJt5XLhEXzHztsoZ0HcWo9GHJJsHcJM/8GM7AoGAWzr3nT3wwlLoBjOdFjNwnBVuhvsmhnKizwHZhD00YZ9Be72eLpK93Qk2Dpg902EAERdp0Z5vCI3rpmpWNiI0+v2CuATkS5MFhmi4UkAmz3/BwQs6bMdB6p+Cf3rEJTVp9VGlySOqKchueTo1zucDOD4Y/bKmIJvrj2Okre3zrssCgYBgi9AAfeaLo4ALgw51Gadxtl0LMD4lQJerVZktfIvr/QttK/RlrnLXjDuyWP0qmb2qa9wFTA6e9mo90OQ+mz8Ze5mVxudEt+wPM/kaBCcrcFLZHvF3Q1ttJR1MdyQU1/s1jwASJfAHfB35n+Fnab/c+xNdm0xmZ1YwVuQkRGNjXwKBgB1HwcjqW5PrNFI84F6j7hXWu5sLYk/gfg9FD5sdmuyff2dF3K69Pz+sa9YAk89tPTECG0ZkxJGKdgMfUJP3acQq1m7cfH42vtRhwYTD3NYRPv+x1jMz+qOxlxQMk06vvTr0WHps1UH3x8+8MzLSpE6l1ixAdLigL+HmciaDA/63\n-----END PRIVATE KEY-----'  # 应用私钥（默认从两个TXT文件中读取）
        self.alipay_public_key_string = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5+VdFftdI5tx07pkt+4etlirJm2XXmETQ3gfIaITGxicOMbb8Psvvl1TOLmC8Z+F9bqGBc1dqoN/TylKZZDB85VSOSV2F+4tAby9uKaYyt4KobAv2+5Qyyq2qumh3Bf8njLcNtN28eBq/pFvM2aDATj8Cv+ggSjNf/YcX2/xqIjsoxaGntipbzJXPIgbwfVDVBzcsCOj+GDDxTJ7OyS7XIlZ/jQNp5Jx/HcrjYyOMOkMnxXBiudFmyPE0J4J0ztVPU2r784xw0uQyUjibXnaNo5Gs9x+j9myskT7w9tOO26o6ganPzRzb8NGxZfYxHSWuuBxqLO93hRBm8eLYgU77QIDAQAB\n-----END PUBLIC KEY-----'  # 支付宝公钥
        self.alipay = AliPay(
            appid=appid,
            app_notify_url=url,
            app_private_key_string=self.app_private_key_string,
            alipay_public_key_string=self.alipay_public_key_string,
            sign_type="RSA2",
            debug=False)

    def pay(self, out_biz_no, payee_account, amount, payee_real_name=None, remark=u'热量星球提现',
            payer_show_name=u'热量星球', payee_type="ALIPAY_LOGONID"):
        '''
        发起转账
        :param payee_account: 收款方账户
        :param amount: 转账金额
        :param payee_real_name:
        :param remark: 收款方姓名
        :param payer_show_name: 转账备注
        :param payee_type: 付款方姓名
        :return:
        '''
        try:
            result = self.alipay.api_alipay_fund_trans_toaccount_transfer(
                out_biz_no=out_biz_no,
                payee_type=payee_type,
                payee_account=payee_account,
                amount=amount,
                payee_real_name=payee_real_name,
                remark=remark,
                payer_show_name=payer_show_name
            )
        except Exception, e:
            # 签名错误
            return False, u'支付宝提现系统升级中！'
        # 转账成功
        if result.get('code') == '10000':
            if result.get('msg') == "Success":
                return True, result.get('order_id', '')
        else:
            if result.get('code') == '20000':
                # 签名错误
                return False, u'服务暂时不可用！'
            elif result.get('code') == '40004':
                # 签名错误
                print result.get('sub_msg')
                return False, result.get('sub_code')
            else:
                # 签名错误
                return False, u'支付宝提现系统升级中！'


if __name__ == '__main__':
    Payment_obj = Payment('2019101568374962', '')
    Payment_obj.pay('201910156837496211', '18680058921', 0.3)
