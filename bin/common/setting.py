import json
import logging

from bin.common.login import Login


class SettingSystem:
    """通过POST向接口：'http://corp.dinghuo123.com/v2/setting/update'
       发送update后的data{}配置，其他设置更改以此类推"""

    def __init__(self, ydh):
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}

    def update_customer(self):
        url = 'http://corp.dinghuo123.com/v2/setting/update'
        data = {}
        data.update({'orderName': '客户'})
        data.update({'isEnabledCustomRegion': 1})
        r = self.s.post(url, data=data, headers=self.headers)
        response = r.json()
        if response['code'] == 200:
            pass
        else:
            logging.error('update customer setting failed')
            logging.error(r.text)

    def update_goods(self):
        url = 'http://corp.dinghuo123.com/v2/setting/update'
        data = {}
        data.update({'isUseProductImage': 1})
        data.update({'isUseMinQuantity': 0})
        data.update({'isUseMaxQuantity': 0})
        data.update({'isUseProductBrand': 1})
        data.update({'isUseProductWeight': 0})
        data.update({'isUseProductDefined': 0})
        data.update({'productTags': json.dumps(
            [{"id": 0, "tagName": "新品上架", "tagId": 1}, {"id": 0, "tagName": "热卖推荐", "tagId": 2},
             {"id": 0, "tagName": "清仓优惠", "tagId": 3}, {"tagId": 4, "tagName": ""}, {"tagId": 5, "tagName": ""}])})
        data.update({'productProperty': json.dumps(
            {"property1": '', "property2": '', "property3": '', "property4": '', "property5": '',
             "property6": '', "property7": '', "property8": '', "property9": '', "property10": ''})})
        r = self.s.post(url, data=data, headers=self.headers)
        response = r.json()
        if response['code'] == 200:
            pass
        else:
            logging.error('update goods setting failed')
            logging.error(r.text)

    def update_fund_account(self):
        url = 'http://corp.dinghuo123.com/v2/setting/update'
        data = {}
        data.update({'fundAccountSettings': json.dumps([{"baseId": 1, "name": "预付款账户", "code": "0001", "canPay": "1",
                                                         "canRecharge": "1", "enableStatus": "1", "autoAuditFlag": "1"},
                                                        {"baseId": 2, "name": "返点账户", "code": "0002", "canPay": "1",
                                                         "canRecharge": "0", "enableStatus": "1", "autoAuditFlag": "1"},
                                                        {"baseId": 3, "name": "保证金账户", "code": "0003", "canPay": "0",
                                                         "canRecharge": "1", "enableStatus": "1",
                                                         "autoAuditFlag": "0"}])})
        r = self.s.post(url, data=data, headers=self.headers)
        response = r.json()
        if response['code'] == 200:
            pass
        else:
            logging.error('update fund account setting failed')
            logging.error(r.text)

    def get_messages_setting(self):
        url = 'https://corp.dinghuo123.com/v2/messageSetting/get'
        r = self.s.get(url, headers=self.headers)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error('get messages setting failed')
            logging.error(r.text)

    def update_messages_setting(self):
        # self.get_messages_setting()
        url = 'https://corp.dinghuo123.com/v2/messageSetting/update'
        data = {
            'signature': '',
            'companyName': 'test@dinghuo123.com',
            'loginUrl': 'https://sso.dinghuo123.com',
            'contacts': '铱云测试部',
            'mobile': '12345678901',
            'isAllOrderToAgent': 'false',
            'isAllOrderToCorp': 'false',
            'isFundsToAgent': 'false',
            'isFundsToCorp': 'false',
            'isFeedbackToAgent': 'false',
            'isFeedbackToCorp': 'false',
            'isNoticeToAgent': 'false',
            'isNoticeToCorp': 'false'
        }
        r = self.s.post(url, data=data, headers=self.headers)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error('update message setting failed')
            logging.error(r.text)

    def initialize(self, init_type):
        # init_type=0 全部数据初始化
        # init_type=1 订单数据初始化
        url = 'https://corp.dinghuo123.com/v2/setting/initialize'
        data = {'initType': init_type, 'password': 123456}
        r = self.s.post(url, data=data, headers=self.headers)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error('initialize setting failed')
            logging.error(r.text)


if __name__ == '__main__':
    ydh = Login()
    ydh.login('11299996612', '123456')
    setting_sys = SettingSystem(ydh)
    setting_sys.update_customer()
    setting_sys.update_goods()
    setting_sys.update_fund_account()
    setting_sys.update_messages_setting()
    setting_sys.get_messages_setting()
    # setting_sys.initialize(0)
