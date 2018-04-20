import logging
import os
import json
import datetime
from random import randrange
from bin import config
from bin.common.common import RunTimeConfig
from pyexcel_xlsx import get_data, save_data
from collections import OrderedDict
from bin.common.common import Login


def set_self_levels():
    # randint() include the endpoint but randrange() not
    levels = []
    discount = ['0.1', '0.2', ' 0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
    for i in range(randrange(config.customer_level_lower_limit, config.customer_level_upper_limit)):
        levels.append(['level_' + str(i), discount[randrange(0, len(discount))]])
    return levels

self_levels = set_self_levels()


def set_self_departments():
    departments = []
    for i in range(randrange(config.customer_department_lower_limit, config.customer_department_upper_limit)):
        departments.append('department_' + str(i))
    return departments

self_departments = set_self_departments()


self_address = [u'中国北京北京市东城区科技园清华信息港科研楼',
                u'中国天津天津市和平区科技园清华信息港科研楼',
                u'中国河北石家庄市长安区科技园清华信息港科研楼',
                u'中国山西太原市小店区科技园清华信息港科研楼',
                u'中国内蒙古自治区呼和浩特市新城区科技园清华信息港科研楼',
                u'中国辽宁沈阳市和平区科技园清华信息港科研楼',
                u'中国吉林长春市南关区科技园清华信息港科研楼',
                u'中国上海上海市黄浦区科技园清华信息港科研楼',
                u'中国浙江杭州市上城区科技园清华信息港科研楼',
                u'中国山东济南市历下区科技园清华信息港科研楼',
                u'中国河南郑州市中原区科技园清华信息港科研楼',
                u'中国湖南长沙市芙蓉区科技园清华信息港科研楼',
                u'中国广东广州市天河区科技园清华信息港科研楼',
                u'中国重庆重庆市万州区科技园清华信息港科研楼',
                u'中国云南昆明市五华区科技园清华信息港科研楼']


class Level:

    def __init__(self, ydh):
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}

    def get_levels(self):
        url = 'https://corp.dinghuo123.com/v2/customerType/list'
        r = self.s.get(url, headers=self.headers)
        return len(r.json()['data'])

    def add_levels(self, level):
        url = 'https://corp.dinghuo123.com/v2/customerType/add'
        data = {'name': level[0], 'discountrate': level[1]}
        r = self.s.post(url, headers=self.headers, data=data)
        res = r.json()
        if res['code'] == 200 and res['message'].startswith(u'操作成功'):
            pass
        elif res['code'] == 250 and res['message'].startswith(u'已有同名级别'):
            pass
        else:
            logging.error('add level {} failed'.format(level))
            logging.error(r.text)

    def init_levels(self):
        if self.get_levels() > config.customer_level_lower_limit:
            logging.warning("It doesn't need to add level any more")
            return

        for self_level in self_levels:
            self.add_levels(self_level)


class Department:

    def __init__(self, ydh):
        self.s = ydh .get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}

    def get_departments(self):
        url = 'https://corp.dinghuo123.com/v2/customRegion/list'
        r = self.s.get(url, headers=self.headers)
        return len(r.json()['data']['1'])

    def add_departments(self, department):
        url = 'https://corp.dinghuo123.com/v2/customRegion/add'
        data = {'name': department, 'parentTypeId': 0}
        r = self.s.post(url, headers=self.headers, data=data)
        res = r.json()
        if res['code'] == 200 and res['message'].startswith('操作成功'):
            pass
        elif res['code'] == 525 and res['message'].startswith("自定义部门不能重复"):
            pass
        else:
            logging.error('add department {} failed'.format(department))
            logging.error(r.text)

    def init_departments(self):
        if self.get_departments() > config.customer_department_lower_limit:
            logging.warning("It doesn't need to add department any more")
            return
        else:
            for self_department in self_departments:
                self.add_departments(self_department)


class Staff:

    def __init__(self, ydh):
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}

    def add_staffs(self, limit):
        url = 'https://corp.dinghuo123.com/v2/companyUser/add'
        staff_name = 'staff_1'
        staff_account = 'ie33330000'
        for i in range(limit):
            data = {'userName': staff_account + str(i),
                      'password': '111111',
                      'confirmpwd': '111111',
                      'realName': staff_name + str(i),
                      'mobile': 13800038000,
                      'companyDepartmentName': 2080952,
                      'isCareArea': 0,
                      'roles': [3],
                      'customRegionSwitch': 2,
                      'areasArray': '',
                      'companyDepartmentId': 2080952,
                      'customRegionEntries': ["0"]}

            r = self.s.post(url, headers=self.headers, data=data)
            resp = r.json()
            if resp['code'] == 200 and resp['message'].startswith('操作成功'):
                print("add success")
            else:
                logging.error(r.text)


class Customers:

    def __init__(self, ydh):
        self.ydh = ydh
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.dbid = ydh.get_dbid()
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = path + '/../data/customers/'
        self.xlsx = self.data_path + self.dbid + '_customers'
        self.customer_template = path + "/../templates/客户导入模板.xlsx"
        self.upload_file_name = []
        self.limit = 10000

    def get_file_token(self):
        return RunTimeConfig(self.ydh).file_token

    def __generate(self, limit, row_num, filename, customer_name):
        customer_data = get_data(self.customer_template)
        customer_columns = customer_data['客户数据']
        for i in range(limit):
            customer_data = ['' for j in range(row_num)]
            customer_data[0] = customer_name + str(i)     # 客户名称
            customer_data[2] = self_address[randrange(0, len(self_address))]  #
            customer_data[3] = self_levels[randrange(0, len(self_levels))][0]
            customer_data[9] = self_departments[randrange(0, len(self_departments))]
            customer_data[14] = customer_name + str(i)
            customer_data[16] = '12345678901'
            customer_data[19] = u'默认仓'
            customer_data[22] = customer_name + str(i)
            customer_data[23] = '123456'
            customer_columns.append(customer_data)
        new_customer_data = OrderedDict()
        new_customer_data.update({'客户数据': customer_columns})
        save_data(filename, new_customer_data)

    def generate_xlsx(self):
        row_num = 25
        if len(self.get_customer_files()) * self.limit > config.customer_upper_limit:
            logging.warning("no need to generate customer xlsx")
            return

        count = randrange(config.customer_lower_limit, config.customer_upper_limit)
        logging.warning('customer numbers: {}'.format(count))
        file_counts = int(count / self.limit)
        remainder_count = int(count % self.limit)
        for file_count in range(file_counts):
            filename = self.xlsx + '_' + str(file_count) + '.xlsx'
            customer_name = 'xxC' + self.dbid + str(file_count)
            self.__generate(self.limit, row_num, filename, customer_name)
        if remainder_count:
            filename = self.xlsx + '_remainder.xlsx'
            customer_name = 'xxC' + self.dbid + '999'
            self.__generate(remainder_count, row_num, filename, customer_name)

    def get_customer_files(self):
        customer_files = []
        for root, dirs, files, in os.walk(self.data_path):
            for name in files:
                if name.startswith(self.dbid):
                    customer_files.append(self.data_path + name)
        return customer_files

    def get_customer_total_count(self, customer_status=0):
        url = 'https://corp.dinghuo123.com/v2/customer/list?currentPage=1&pageSize=30&customer_status=%s' % customer_status
        r = self.s.get(url, headers=self.headers)
        return int(r.json()['data']['totalCount'])

    def get_customers(self, customer_status=0, page_size=10):
        url = 'https://corp.dinghuo123.com/v2/customer/list?customerStatus={0}&currentPage=1&pageSize={1}'.format(customer_status, page_size)
        r = self.s.get(url, headers=self.headers)
        return r.json()['data']['items']

    def __upload(self, url, filename):
        fp = open(filename, 'rb')
        files = {'file': (filename.split('/')[-1], fp, 'application/vnd.ms-excel')}
        r = self.s.post(url, headers=self.headers, files=files)
        fp.close()
        res = r.json()
        if res['code'] == 200:
            return res['data']['upload_file_name']
        else:
            logging.error('upload customer xlsx {} failed'.format(filename))
            logging.error(r.text)
            return None

    def upload_xlsx(self, filename):
        url = 'https://file.dinghuo123.com/corp/customerImport/previewTemplate?file_token={0}'.format(self.get_file_token())
        self.s.option(url)  # 为什么要发送这个请求？
        return self.__upload(url, filename)

    def import_customers(self):
        url = 'https://file.dinghuo123.com/corp/customerImport/importCustomer?file_token={0}'.format(self.get_file_token())
        self.s.option(url)

        for filename in self.get_customer_files():
            upload_file_name = self.upload_xlsx(filename)
            data = {'upload_file_name': upload_file_name, 'templateType': 'default'}
            r = self.s.post(url, headers=self.headers, data=data)
            if r.json()['code'] == 200 and r.json()['message'].startswith('操作成功'):
                logging.warning("import customer file: {0}".format(filename))
            else:
                logging.error("import customer {0} failed".format(upload_file_name))
                logging.error(r.text)

    def export_customers(self):
        url = 'https://file.dinghuo123.com/corp/customerImport/exportCustomer?&file_token={0}'.format(self.get_file_token())
        r = self.s.post(url, headers=self.headers)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error("export customer failed")
            logging.error(r.text)

    def init_customers(self):
        if self.get_customer_total_count() > config.customer_lower_limit:
            logging.warning('no need to init customer')
            return
        self.generate_xlsx()
        self.import_customers()


if __name__ == '__main__':
    ydh = Login()
    ydh.login('15815568853', '123456')
    staff = Staff(ydh)
    staff.add_staffs(3)
    # department = Department(ydh)
    # department.init_departments()
    # level = Level(ydh)
    # level.init_levels()
    # customer = Customers(ydh)
    # customer.init_customers()
    #
    # now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # fake_file = '../../data/temp/fake_customer_' + now + '.txt'
    # with open(fake_file, 'wb') as f:
    #     f.write('customer_id customer_name customer_level_id')
    #     f.write('\n')
    #
    # for customer in customer.get_customers(page_size=200):
    #     customer_id = customer['id']
    #     customer_name = customer['name']
    #     customer_level_id = customer['customerTypeId']
    #     with open(fake_file, 'ab') as f:
    #         f.write(str(customer_id) + '' + str(customer_name) + '' + str(customer_level_id))
    #         f.write('\n')
