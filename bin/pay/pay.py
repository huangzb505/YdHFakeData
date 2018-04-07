# -*- coding:utf-8 -*-
import logging
import os
from collections import OrderedDict

from pyexcel_xlsx import get_data, save_data
from random import randrange
from bin.common.common import RunTimeConfig
from bin.common.login import Login
from bin import config
from bin.customer.customer import Customers


class Pay:
    def __init__(self, ydh):
        self.s = ydh.get_session()
        self.ydh = ydh
        self.dbid = ydh.get_dbid()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.customers = Customers(ydh)
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = path + '/../data/payment/'
        self.pay_template = path + u'/../templates/资金账户模板.xlsx'

    def get_file_token(self):
        return RunTimeConfig(self.ydh).file_token

    def get_online_pay_account(self):
        url = 'https://corp.dinghuo123.com/app/onlinePayAccount?action=onlinePayAccountJson'
        r = self.s.get(url)
        return r.json()

    def save_online_pay_account(self, platform):
        online_pay_account = self.get_online_pay_account()
        if platform == 1:
            if len(online_pay_account['data']['weixinpay']):
                return
        elif platform == 2:
            if len(online_pay_account['data']['alipay']):
                return

        url = 'https://corp.dinghuo123.com/app/onlinePayAccount?action=saveOrUpdate '
        if platform == 1:
            data = {'userName': 'test@dinghuo123.com',
                    'appSecret': '1234567890123456',
                    'merchantAccount': 'test@dinghuo123.com',
                    'merchantKey': '1234567890123456',
                    'status': 1,
                    'platform': 1
                    }
        elif platform == 2:
            data = {'userName': 'test@dinghuo123.com',
                    'merchantAccount': '1234567890123456',
                    'merchantKey': '1234567890123456',
                    'platform': 2,
                    'status': 1
                    }
        else:
            logging.error('unknow platform')
            return
        r = self.s.post(url, headers=self.headers, data=data)
        response = r.json()
        if response['code'] == 200:
            pass
        else:
            logging.error('save online pay account failed')
            logging.error(r.text)

    def save_company_bank(self):
        url = 'https://corp.dinghuo123.com/app/payment?action=bank_list&isPc=true&currentPage=1&pageSize=30'
        r = self.s.get(url)
        if len(r.json()['data']['items']):
            return

        url = 'https://corp.dinghuo123.com/app/payment?action=saveBank'
        data = {'bankName': u'招商银行',
                'bankAccount': self.ydh.mobile,
                'bankAccountName': 'AutoTest'}
        r = self.s.post(url, headers=self.headers, data=data)
        response = r.json()
        if response['code'] == 200:
            pass
        else:
            logging.error('save company bank failed')
            logging.error(r.text)

    def generate_payment_xlsx(self):
        if len(self.get_payment_files()) == len(self.customers.get_customer_files()):
            logging.warning('no need to generate payment xlsx')
            return

        fund_account_code = ['0001', '0002']
        fund_account_abstract = [u'现金充值', u'其他充值', u'销售返点', u'退款', u'订单付款', u'其他付款']

        for customer_file in self.customers.get_customer_files():
            customer_data = get_data(customer_file)
            customer_columns = list(customer_data[u'客户数据'])

            fund_account_data = get_data(self.pay_template)
            fund_account_data_columns = list(fund_account_data['Sheet1'])
            for customer in customer_columns[2:]:
                fund_account_data_column = [customer[0],
                                            fund_account_code[randrange(0, len(fund_account_code))],
                                            randrange(500, 10000),
                                            fund_account_abstract[randrange(0, len(fund_account_abstract))]]
                fund_account_data_columns.append(fund_account_data_column)
            new_fund_account_data = OrderedDict()
            new_fund_account_data.update({'Sheet1': fund_account_data_columns})
            save_data(customer_file.replace('customers', 'payment'), new_fund_account_data)

    def get_payment_count(self):
        url = 'https://corp.dinghuo123.com/app/payment?action=getPaymentCount'
        r = self.s.get(url, headers=self.headers)
        count = r.json()['data']['totalCount']
        return int(count)

    def get_payment_files(self):
        payment_files = []
        for root, dirs, files in os.walk(self.data_path):
            for name in files:
                if name.startswith(self.dbid):
                    payment_files.append(self.data_path + name)
        return payment_files

    def import_payment(self):
        if self.get_payment_count() >= config.payment_limit:
            logging.warning('no need to import payment')
            return
        sub = config.payment_limit - self.get_payment_count()
        for i in range(sub):
            for filename in self.get_payment_files():
                url = 'https://file.dinghuo123.com/corp/fundAccountImport/checkSign?file_token=%s' % self.get_file_token()
                r = self.s.post(url, headers=self.headers)
                check_sign = r.json()['data']['checkSign']

                url = 'https://file.dinghuo123.com/corp/fundAccountImport/importExcel?file_token=%s' % self.get_file_token()
                fp = open(filename, 'rb')
                files = {'file': (filename.split('/')[-1], fp, 'application/vnd.ms-excel')}
                data = {'checkSign': check_sign}
                r = self.s.post(url, headers=self.headers, files=files, data=data)
                fp.close()
                response = r.json()
                if response['code'] == 200:
                    logging.warning('import payment file: %s' % filename)
                else:
                    logging.error('import %s failed' % filename)
                    logging.error(r.text)

        # self.import_payment()

    # 订单收款统计列表
    def order_payment_list(self, start_time, end_time):
        data = {'start_time': start_time, 'end_time': end_time}
        url = 'https://corp.dinghuo123.com/app/orderPayment?action=list&currentPage=1&pageSize=30&beginDate=%(start_time)s&endDate=%(end_time)s' % data
        r = self.s.post(url)
        if r.json()['code'] == 200:
            return r.json()
        else:
            logging.error(r.text)
            return None

    # 订单收款统计导出
    def export_order_payment_report(self, start_time, end_time):
        data = {'start_time': start_time, 'end_time': end_time, 'file_token': self.get_file_token()}
        url = 'https://file.dinghuo123.com/corp/orderPayment/queryPaymentReportExporter?action=queryPaymentReport&beginTime=%(start_time)s&endTime=2%(end_time)s&file_token=%(file_token)s' % data

        self.s.options(url)

        r = self.s.post(url)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error(r.text)

    # 收支明细列表
    def payment_list(self, start_time, end_time):
        data = {'start_time': start_time, 'end_time': end_time}
        url = 'https://corp.dinghuo123.com/app/payment?action=list&currentPage=1&pageSize=30&beginDate=%(start_time)s&endDate=%(end_time)s' % data
        r = self.s.post(url)
        if r.json()['code'] == 200:
            return r.json()
        else:
            logging.error(r.text)
            return None

    # 收支明细导出
    def export_order_payment_list(self, start_time, end_time):
        data = {'start_time': start_time, 'end_time': end_time, 'file_token': self.get_file_token()}
        url = 'https://file.dinghuo123.com/corp/orderPayment/exporterList?beginTime=%(start_time)s&endTime=%(end_time)s&file_token=%(file_token)s' % data

        self.s.options(url)

        r = self.s.post(url)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error(r.text)

    def init_pay(self):
        if self.get_payment_count() > config.payment_limit:
            logging.warning('no need to import payment')
            return
        self.generate_payment_xlsx()
        self.import_payment()


if __name__ == '__main__':
    ydh = Login()
    ydh.login('11299996612', '123456')

    pay = Pay(ydh)
    pay.save_online_pay_account(1)
    pay.save_online_pay_account(2)
    pay.save_company_bank()
    pay.generate_payment_xlsx()
    pay.import_payment()
