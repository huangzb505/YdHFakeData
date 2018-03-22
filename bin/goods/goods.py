import os
import logging
from collections import OrderedDict
from pyexcel_xlsx import get_data, save_data
from bin.common.common import RunTimeConfig
from random import randrange
from bin import config
from bin.common.common import Login

def set_self_brands():
    brands = []
    for i in  range(randrange(config.goods_brand_lower_limit, config.goods_brand_upper_limit)):
        brands.append("brand_" + str(i))
    return brands

self_brands = set_self_brands()


def set_self_categories():
    categories = []
    for i in range(randrange(config.goods_category_lower_limit,config.goods_category_upper_limit)):
        categories.append("category_" + str(i))
    return categories

self_categories = set_self_categories()


class Brand:
    def __init__(self, ydh):
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}

    def get_brands_count(self):
        url = 'https://corp.dinghuo123.com/v2/goodsBrand/list'
        r = self.s.get(url, headers=self.headers)
        return len(r.json()['data'])

    def add_brand(self, brand):
        url = 'https://corp.dinghuo123.com/v2/goodsBrand/add'
        data = {'name': brand}
        r = self.s.post(url, headers=self.headers, data=data)
        res = r.json()
        if res['code'] == 200 or res['code'] == 250:
            pass
        else:
            logging.error("add brand {0} failed".format(brand))
            logging.error(r.text)

    def init_brands(self):
        if self.get_brands_count() > config.goods_brand_lower_limit:
            logging.warning("no need to add brands")
            return
        else:
            for brand in self_brands:
                self.add_brand(brand)


class Categories:

    def __init__(self, ydh):
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}

    def get_categories_count(self):
        url = 'https://corp.dinghuo123.com/v2/goodsType/list'
        r = self.s.get(url, headers=self.headers)
        return len(r.json()['data']['1'])

    def add_category(self, category):
        url = 'https://corp.dinghuo123.com/v2/goodsType/add'
        data = {'name': category, 'parentTypeId': '0'}
        r = self.s.post(url, headers=self.headers, data=data)
        res = r.json()
        if res['code'] == 200 or res['code'] == 250:
            pass
        else:
            logging.error("add category {0} failed".format(category))
            logging.error(r.text)

    def init_categories(self):
        if self.get_categories_count() > config.goods_category_lower_limit:
            logging.error("no need to add categories")
        else:
            for category in self_categories:
                self.add_category(category)


class Goods:

    def __init__(self, ydh):
        self.ydh = ydh
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
        self.dbid = ydh.get_dbid()
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = path + '/../data/goods/'
        self.goods_xlsx = self.data_path + self.dbid() + 'goods'
        self.goods_template = path + u'/../templates/商品基础信息导入模板.xlsx'
        self.limit = 2000

    def get_file_token(self):
        return RunTimeConfig(self.ydh).file_token

    def get_goods_files(self):
        goods_files = []
        for root, dirs, files in os.walk(self.data_path):
            for name in files :
                if name.startswith(self.dbid):
                    goods_files.append(self.data_path + name)
        return goods_files

    def __generate(self, limit, row_num, filename, goods_name):
        goods_data = get_data(self.goods_template)
        goods_columns = goods_data['商品数据']
        for i in range(limit):
            column_data = ['' for j in range(row_num)]
            column_data[0] = goods_name + str(i)
            column_data[1] = goods_name + str(i)
            column_data[2] = str(self_brands[randrange(0, len(self_brands))])
            column_data[3] = str(self_categories[randrange(0, len(self_categories))])
            # column_data[11] = u'相关介绍: 性能测试初始化的商品数据，采用较短的介绍长度'
            column_data[11] = u'件'
            # column_data[17] = u'上架'
            # column_data[19] = str(random.randrange(10, 50))
            # column_data[20] = str(random.randrange(50, 200))
            goods_columns.append(column_data)
            new_goods_data = OrderedDict()
            new_goods_data.update({'商品数据': goods_columns})
            save_data(filename, new_goods_data)






if __name__ == '__main__':
    ydh = Login()
    ydh.login('11299996612', '123456')
    brand = Brand(ydh)
    brand.init_brands()
    category = Categories(ydh)
    category.init_categories()