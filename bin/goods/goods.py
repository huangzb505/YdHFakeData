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
    for i in range(randrange(config.goods_brand_lower_limit, config.goods_brand_upper_limit)):
        brands.append("brand_" + str(i))
    return brands

self_brands = set_self_brands()


def set_self_categories():
    categories = []
    for i in range(randrange(config.goods_category_lower_limit, config.goods_category_upper_limit)):
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


class Category:

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
        self.goods_xlsx = self.data_path + self.dbid + 'goods'
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

    def generate_xlsx(self):
        row_num = 21
        if self.get_goods_files() * self.limit > config.goods_lower_limit:
            logging.warning("no need to generate goods")
            return
        count = randrange(config.goods_lower_limit, config.goods_upper_limit)
        logging.warning('goods number: {0}'.format(count))
        file_counts = int(count / self.limit)
        remainder_count = int(count % self.limit)

        for file_count in range(file_counts):
            filename = self.goods_xlsx + '_' + str(file_count) + '.xlsx'
            goods_name = 'xxP' + self.dbid + str(file_count)
            self.__generate(self.limit, row_num, filename, goods_name)

        if remainder_count:
            filename = self.goods_xlsx + '_remainder.xlsx'
            goods_name = 'xxP' + self.dbid + '999'
            self.__generate(remainder_count, row_num, filename, goods_name)

    def _upload(self, url, filename):
        fp = open(filename, 'rb')
        files = {'file': (filename.split('/')[-1], fp, 'application/vnd.ms-excel')}
        r = self.s.post(url, headers=self.headers, files=files)
        fp.close()
        res = r.json()
        if res['code'] == 200:
            return res['data']['upload_file_name']
        else:
            logging.error('upload goods xlsx {0} failed'.format(filename))
            logging.error(r.text)

    def upload_xlsx(self, filename):
        url = 'https://file.dinghuo123.com/corp/productImport/previewTemplate?file_token={0}'.format(self.get_file_token())
        self.s.options(url)
        self._upload(url, filename)

    def import_goods(self):
        url = 'https://file.dinghuo123.com/corp/productImport/previewTemplate?file_token={0}'.format(self.get_file_token())
        self.s.options(url)

        for file in self.get_goods_files():
            upload_file_name = self.upload_xlsx(file)
            if upload_file_name is None:
                continue
            data = {'upload_file_name': upload_file_name, 'templateType': 'default'}
            r = self.s.post(url, headers=self.headers, data=data)
            res = r.json()
            if res['code'] == 200 and res['message'].startswith('操作成功'):
                logging.warning('upload goods file: {0}'.format(file))
            else:
                logging.error('import goods file {0} failed'.format(upload_file_name))
                logging.error(r.text)

    def get_goods_total_count(self):
        url = 'https://corp.dinghuo123.com/v2/goods/list?currentPage=1&pageSize=30&loadPrice=false'
        r = self.s.get(url, headers=self.headers)
        return int(r.json()['data']['totalCount'])

    def init_goods(self):
        if self.get_goods_total_count() > config.goods_lower_limit:
            logging.warning('no need to init goods')
            return
        else:
            self.generate_xlsx()
            self.import_goods()

    def get_goods(self, goods_status=0, count=1000, page=1):
        url = 'https://corp.dinghuo123.com/v2/goods/list?status={0}&currentPage={1}&pageSize={2}&loadPrice=false'.format(goods_status, page, count)
        r = self.s.get(url, headers=self.headers)
        return r.json()['data']['items']

    def export_goods(self):
        url = 'https://file.dinghuo123.com/corp/productImport/exportProduct?operation=search&&file_token={0}'.format(self.get_file_token())
        r = self.s.post(url, headers=self.headers)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error('export goods failed')
            logging.error(r.text)


if __name__ == '__main__':
    ydh = Login()
    ydh.login('11299996615', '123456')
    brand = Brand(ydh)
    brand.init_brands()
    category = Category(ydh)
    print(category.get_categories_count())
    category.init_categories()
    goods = Goods(ydh)
    item = goods.get_goods()
    print(item)