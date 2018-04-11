import logging
import os
import json
from collections import OrderedDict
from random import randrange
from pyexcel_xlsx import get_data, save_data
from bin.common.common import RunTimeConfig
from bin import config
from bin.common.login import Login
from bin.customer.customer import Customers
from bin.goods.goods import Goods


class Orders:

    def __init__(self, ydh):
        self.ydh = ydh
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.dbid = ydh.get_dbid()
        self.file_num = config.order_file_num
        self.goods_in_order_num = config.goods_in_order_num
        self.customer = Customers(ydh)
        self.customer_data = self.customer.get_customers(page_size=self.file_num)
        self.goods = Goods(ydh)
        self.goods_data = self.goods.get_goods()
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = path + '/../data/orders/'
        self.order_xlsx = self.data_path + self.dbid + '_order'
        self.order_template = path + '/../templates/订单导入单模板.xlsx'
        self.import_rule_id = None

    def get_file_token(self):
        return RunTimeConfig(self.ydh).file_token

    def get_order_files(self):
        order_files = []
        for root, dirs, files in os.walk(self.data_path):
            for name in files:
                if name.startswith(self.dbid):
                    order_files.append(self.data_path + name)
        return order_files

    def get_order_import_rules(self):
        url = 'https://file.dinghuo123.com/corp/orderImport/listRules?submitType=ajax&file_token=%s'.format(self.get_file_token())
        r = self.s.get(url, headers=self.headers)
        for rule in r.json()['data']['list']:
            if rule['ruleName'] == '导入模板':
                self.import_rule_id = rule['id']
                return rule
        return False

    def save_order_import_rules(self):
        if self.get_order_import_rules() is not False:
            logging.warning('found order import rule. no need to save order import rules')
            return

        url = 'https://file.dinghuo123.com/corp/orderImport/saveRule?file_token=%s'.format(self.get_file_token())
        column_mapping = {'orderNum': 0, 'orderMoney': 1, 'freight': 2, 'orderCreateDate': 3,
                          'deliveryDate': 4, 'customerName': 5, 'receiverLabel': 6, 'receiverName': 7,
                          'receiverMobile': 8, 'shippingAddress': 9, 'shippingAddrProvince': 10,
                          'shippingAddrCity': 11, 'shippingAddrArea': 12, 'orderRemark': 13,
                          'productCode': 14, 'productName': 15, 'productSpec': 16, 'productPrice': 17,
                          'qty': 18, 'productRemark': 19}
        rule_json = {'importRuleName': '订单导入模板',
                     'ruleType': '1',
                     'totalCount': 20,
                     'header': [{'columnName': '订单编号*', 'index': 0}, {'columnName': '订单金额', 'index': 1},
                                {'columnName': '运费', 'index': 2}, {'columnName': '下单日期', 'index': 3},
                                {'columnName': '交货日期', 'index': 4}, {'columnName': '下单客户名称', 'index': 5},
                                {'columnName': '收货单位', 'index': 6}, {'columnName': '收货联系人*', 'index': 7},
                                {'columnName': '收货联系电话', 'index': 8}, {'columnName': '收货地址*', 'index': 9},
                                {'columnName': '收货地址-省', 'index': 10}, {'columnName': '收货地址-市', 'index': 11},
                                {'columnName': '收货地址-区', 'index': 12}, {'columnName': '订单备注', 'index': 13},
                                {'columnName': '商品编码*', 'index': 14}, {'columnName': '商品名称*', 'index': 15},
                                {'columnName': '商品规格', 'index': 16}, {'columnName': '商品单价*', 'index': 17},
                                {'columnName': '商品数量*', 'index': 18}, {'columnName': '商品备注', 'index': 19}],
                     'columnMapping': json.dumps(column_mapping)}
        data = {'rule_json': json.dumps(rule_json)}
        r = self.s.post(url, headers=self.headers, data=data)
        if r.json()['code'] == 200:
            return True
        else:
            logging.error("save order rule failed")
            logging.error(r.text)
            return False

    def __generate(self, limit, row_num, filename, order_num, file_count):
            order_data = get_data(self.order_template)
            order_columns = order_data['订单归集']
            for order_num_count in range(limit):
                good_subscript = randrange(0, len(self.goods_data) - self.goods_in_order_num)
                for goods_count in range(0, self.goods_in_order_num):
                    column_data = ['' for j in range(row_num)]
                    column_data[0] = order_num + str(order_num_count)
                    column_data[5] = self.customer_data[file_count]['name']
                    column_data[7] = self.customer_data[file_count]['contactor']
                    column_data[8] = '11111111111'
                    column_data[9] = self.customer_data[file_count]['area']
                    column_data[10] = '北京市'
                    column_data[11] = '北京市'
                    column_data[12] = '东城区'
                    column_data[14] = self.goods_data[good_subscript + goods_count]['code']
                    column_data[15] = self.goods_data[good_subscript + goods_count]['name']
                    column_data[17] = self.goods_data[good_subscript + goods_count]['marketPrice']
                    column_data[18] = randrange(1, 50)
                    order_columns.append(column_data)

            new_order_data = OrderedDict()
            new_order_data.update({'订单归集': order_columns})
            save_data(filename, new_order_data)

    def generate_xlsx(self):
        if len(self.get_order_files()) == self.file_num:
            logging.warning('no need to generate order xlsx')
            return
        count = randrange(config.order_lower_limit, config.order_upper_limit)
        limit = int(count / self.file_num)
        logging.warning('orders number:{0}'.format(count))

        row_num = 20

        for file_count in range(self.file_num):
            filename = self.order_xlsx + '_' + str(file_count) + '.xlsx'
            order_num = 'xx0' + self.dbid + str(file_count)
            self.__generate(limit, row_num, filename, order_num, file_count)

    def _upload(self, url, filename):
        fp = open(filename, 'rb')
        files = {'file': (filename.split('/')[-1], fp, 'application/vnd.ms-excel')}
        data = {'id': self.import_rule_id}
        r = self.s.post(url, headers=self.headers, data=data, files=files)
        fp.close()
        res = r.json()
        if res['code'] == 200:
            return res['data']['upload_file_name']
        else:
            logging.error("upload order xlsx {0} failed".format(filename))
            logging.error(r.text)
            return None

    def upload_xlsx(self, filename):
        url ='https://file.dinghuo123.com/corp/orderImport/previewImport?isUploadFile=true&file_token=%s'.format(self.get_file_token())
        self.s.options(url)
        return self._upload(url, filename)

    def get_order_total_count(self):
        url = 'https://corp.dinghuo123.com/v2/order/list?currentPage=1&pageSize=30'
        r = self.s.get(url, headers=self.headers)
        return r.json()['data']['totalCount']

    def get_orders(self, current_page=1, page_size=30):
        url = 'https://corp.dinghuo123.com/v2/order/list?currentPage={0}&pageSize={1}'.format(current_page, page_size)
        r = self.s.get(url, headers=self.headers)
        return r.json()['data']['items']

    def get_order_detail(self, order_num):
        url = 'https://corp.dinghuo123.com/v2/order/get?orderNum=%s&promotionDetail=false'.format(order_num)
        r = self.s.get(url, headers=self.headers)
        return r.json()

    def import_order(self, need_audit=0):
        if self.get_order_total_count() >= config.order_lower_limit:
            logging.warning('no need to import orders')
            return

        url = 'https://file.dinghuo123.com/corp/orderImport/save?file_token=%s'.format(self.get_file_token())
        self.s.options(url)

        for index, filename in enumerate(self.get_order_files()):
            upload_filename = self.upload_xlsx(filename)
            if upload_filename is None:
                continue
            data = {'id': self.import_rule_id,
                    'customerId': self.customer_data[index]['id'],
                    'importType': '1',
                    'needAudit': str(need_audit),
                    'filePath1': upload_filename}
            r = self.s.post(url, headers=self.headers, data=data)
            if r.json()['code'] == 200 and r.json()['message'].startswith('操作成功'):
                logging.warning('import order file: {0}'.format(filename))
            else:
                logging.error('import goods {0} failed  '.format(upload_filename))
                logging.error(r.text)

    # 发货统计列表
    def logistics_reconciliation_list(self, start_time, end_time):
        data = {'start_time': start_time, 'end_time': end_time}
        url = 'https://corp.dinghuo123.com/v2/logisticsReconciliation/list?deliverBeginDate=%(start_time)s&deliverEndDate=%(end_time)s&currentPage=1&pageSize=30' % data
        r = self.s.post(url)
        if r.json()['code'] == 200:
            return r.json()
        else:
            logging.error(r.text)
            return None

    # 发货统计导出
    def export_logistics_reconciliation(self, start_time, end_time):
        data = {'start_time': start_time, 'end_time': end_time, 'file_token': self.get_file_token()}
        url = 'https://file.dinghuo123.com/corp/logisticsReconciliation/export?forward=data&deliverBeginDate=%(start_time)s&deliverEndDate=%(end_time)s&totalCount=0&file_token=%(file_token)s' % data

        self.s.options(url)

        r = self.s.post(url)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error(r.text)

    def init_orders(self):
        if self.get_order_total_count() >= config.order_lower_limit:
            logging.warning('orders are enough, no need to import order')
            return
        self.save_order_import_rules()
        self.get_order_import_rules()
        self.generate_xlsx()
        self.import_order(need_audit=1)


if __name__ == '__main__':
    ydh = Login()
    ydh.login('334488096', '111111')

    orders = Orders(ydh)
    orders.init_orders()



