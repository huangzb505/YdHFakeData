# -*- coding:utf-8 -*-
import datetime
import json
import logging
import time


from random import randint
from bin.common.login import Login
from bin.goods.goods import Goods
from bin import config
from bin.util import datetime_earlier
from bin.util import datetime_later


class Promotion:

    def __init__(self, ydh):
        self.s = ydh.get_session()
        self.dbid = ydh.get_dbid()
        self.ydh = ydh
        self.goods = Goods(ydh)
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.combined_goods_start_page = 1
        self.combined_goods_num = config.combined_promotion_product_count

    def get_promotion_total_count(self, promotion_type):
        url = 'https://corp.dinghuo123.com/v2/promotion/list?' \
              'type={}&showStatusCode=0&currentPage=1&pageSize=30'.format(promotion_type)
        r = self.s.get(url, headers=self.headers)
        if r.json()['code'] == 200:
            return r.json()['data']['totalCount']
        else:
            logging.error('get promotion total count failed')
            logging.error(r.text)
            return False

    def get_promotions(self, promotion_type, count):
        url = 'https://corp.dinghuo123.com/v2/promotion/list?' \
              'type={}&showStatusCode=0&currentPage=1&pageSize={}'.format(promotion_type, count)
        r = self.s.get(url, headers=self.headers)
        if r.json()['code'] == 200:
            return r.json()['data']['items']
        else:
            logging.error('get promotions failed')
            logging.error(r.text)
            return False

    def add_product_promotion(self):
        while self.get_promotion_total_count(promotion_type=1) < config.promotion_limit:
            for goods_data in self.goods.get_goods(count=config.promotion_limit, page=self.combined_goods_num * 2):
                url = 'https://corp.dinghuo123.com/v2/promotion/add'
                data = {'isMulti': '0',
                        'showPromotionInfo': '90',
                        'customerTypeIds': '["0"]',
                        'type': '1',
                        'productIds': '["{}"]'.format(goods_data['id']),
                        'startTime': datetime_earlier(datetime.datetime.now(), days=1).strftime('%Y-%m-%d %H:%M:%S'),
                        'endTime': datetime_later(datetime.datetime.now(), days=3650).strftime('%Y-%m-%d %H:%M:%S'),
                        'promotionInfo': '{"promotionDiscount":90}',
                        'method': '3',
                        'countryId': '0',
                        'provinceId': '0',
                        'cityId': '0'}
                r = self.s.post(url, headers=self.headers, data=data)
                if r.json()['code'] == 200:
                    pass
                else:
                    logging.error('add product promotion failed')
                    logging.error(r.text)

    def add_order_promotion(self):
        while self.get_promotion_total_count(promotion_type=2) < config.promotion_limit:
            url = 'https://corp.dinghuo123.com/v2/promotion/add'
            meet_money = randint(500, 2000)
            minus_money = randint(10, 50)
            data = {'isMulti': '0',
                    'showPromotionInfo': '{}'.format(minus_money),
                    'customerTypeIds': '["0"]',
                    'type': '2',
                    'startTime': datetime_earlier(datetime.datetime.now(), days=1).strftime('%Y-%m-%d %H:%M:%S'),
                    'endTime': datetime_later(datetime.datetime.now(), days=3650).strftime('%Y-%m-%d %H:%M:%S'),
                    'promotionInfo': '{"meetMoney":{},"minusMoney":{}}'.format(meet_money, minus_money),
                    'method': '4',
                    'countryId': '0',
                    'provinceId': '0',
                    'cityId': '0'}
            r = self.s.post(url, headers=self.headers, data=data)
            if r.json()['code'] == 200:
                pass
            else:
                logging.error('add order promotion failed')
                logging.error(r.text)

    def add_combined_promotion(self):
        goods_data = []
        for i in range(self.combined_goods_num):
            goods_data.append(self.goods.get_goods(count=config.combined_promotion_limit,
                                                   page=self.combined_goods_start_page + i))
        while self.get_promotion_total_count(promotion_type=3) < config.combined_promotion_limit:
            for i in range(config.combined_promotion_limit):
                url = 'https://corp.dinghuo123.com/v2/promotion/add'
                meet_count = randint(10, 20)
                gift_count = randint(1, 10)
                product_list = []
                for num in range(self.combined_goods_num):
                    product_list.append({"productId": goods_data[num][i]['id'],
                                         "productCode": goods_data[num][i]['code'],
                                         "productName": goods_data[num][i]['name'],
                                         "productSpec": "",
                                         "customAttributeStitch": ""})
                promotion_info = {"meetCount": meet_count,
                                  "promotionGiftId": goods_data[-1][i]['id'],
                                  "promotionGiftCount": gift_count}
                data = {'name': time.time(),
                        'promotionBy': 1,
                        'isMulti': '0',
                        'showPromotionInfo': '{}'.format(gift_count),
                        'type': '3',
                        'productList': json.dumps(product_list),
                        'startTime': datetime_earlier(datetime.datetime.now(), days=1).strftime('%Y-%m-%d %H:%M:%S'),
                        'endTime': datetime_later(datetime.datetime.now(), days=3650).strftime('%Y-%m-%d %H:%M:%S'),
                        'promotionInfo': json.dumps(promotion_info),
                        'method': '1',
                        'customerTypeIds': '["0"]'}
                r = self.s.post(url, headers=self.headers, data=data)
                if r.json()['code'] == 200:
                    pass
                elif r.json()['code'] == 250:
                    pass
                elif r.json()['code'] == 500 and r.json()['message'] == u'最多支持30条组合促销同时生效':
                    pass
                else:
                    logging.error('add combined promotion failed')
                    logging.error(r.text)

    def discard_promotion(self, promotion_id):
        discard_url = 'https://corp.dinghuo123.com/v2/promotion/discard?ids=[{}]'.format(promotion_id)
        r = self.s.get(discard_url, headers=self.headers)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error('discard promotion {} failed'.format(promotion_id))
            logging.error(r.text)

    def delete_promotion(self, promotion_id):
        delete_url = 'https://corp.dinghuo123.com/v2/promotion/delete?ids=[{}]'.format(promotion_id)
        r = self.s.post(delete_url, headers=self.headers)
        if r.json()['code'] == 200:
            pass
        else:
            logging.error('delete promotion {} failed'.format(promotion_id))
            logging.error(r.text)

    def delete_promotions(self, promotion_type):
        promotions = self.get_promotions(promotion_type=promotion_type,
                                         count=self.get_promotion_total_count(promotion_type=promotion_type))
        for item in promotions:
            self.discard_promotion(item['id'])
            self.delete_promotion(item['id'])

    def init_promotion(self):
        if config.delete_promotion_flag:
            self.delete_promotions(promotion_type=3)
            return

        if self.get_promotion_total_count(promotion_type=1) >= config.promotion_limit:
            logging.warning('no need to add product promotion')
        else:
            self.add_product_promotion()

        if self.get_promotion_total_count(promotion_type=2) >= config.promotion_limit:
            logging.warning('no need to add order promotion')
        else:
            self.add_order_promotion()

        if self.get_promotion_total_count(promotion_type=3) >= config.combined_promotion_limit:
            logging.warning('no need to add combined promotion')
        else:
            self.add_combined_promotion()


if __name__ == '__main__':
    ydh = Login()
    ydh.login('11299996612', '123456')

    promotion = Promotion(ydh)
    promotion.init_promotion()







