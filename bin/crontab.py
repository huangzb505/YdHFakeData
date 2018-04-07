# -*- coding:utf-8 -*-
import random
import time
import traceback
import logging

from bin.common.login import Login
from bin.order.order import Orders
from bin.pay.pay import Pay
from bin import config


def main():
    num = random.randint(1, 5)
    for i in range(num):
        start_time = time.time()
        mobile = config.mobile
        for count in range(config.number):
            try:
                logging.info('crontab' + str(mobile + count) + 'data ....')

                ydh = Login()
                ydh.login(str(mobile+count), '123456')

                orders = Orders(ydh)
                pay = Pay(ydh)
                order_num, product_info, customer_info = orders.order_add()
                success = False
                time.sleep(1)
                if success:
                    success = orders.order_audit(order_num, 1)
                time.sleep(1)
                if success:
                    success = orders.order_audit(order_num, 2)
                time.sleep(1)
                if success:
                    success = orders.order_out_storage(order_num, product_info)
                time.sleep(1)
                if success:
                    success = orders.order_deliver(order_num)
                time.sleep(1)

                customer_fund_account = pay.fundAccount_queryCustomerFundAccount(customer_info['id'])
                if customer_fund_account is False:
                    success = False
                time.sleep(1)
                if success:
                    success = pay.fundAccount_initial(customer_info['id'], customer_fund_account)
                time.sleep(1)
                if success:
                    pay.payment_save(product_info['orderPrice'],
                                     order_num, customer_fund_account)
            except Exception:
                exstr = traceback.format_exc()
                print(exstr)
        end_time = time.time()
        cost_time = end_time - start_time
        print("cost {} seconds".format(cost_time))


while True:
    main()
    time.sleep(3600)
