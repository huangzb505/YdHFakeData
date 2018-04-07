# -*- coding:utf-8 -*-
import logging
import time
import traceback

from bin import util
from bin.common.login import Login
from bin.common.register import Register
from bin.common.setting import SettingSystem
from bin.customer.customer import Customers, Level, Department
from bin.goods.goods import Brand, Category, Goods
# from bin.goods.inventory import Inventory
# from bin.goods.purchase import Supplier
# from bin.marketing.ad import Ad
# from bin.marketing.notification import Notification
from bin.marketing.promotion import Promotion
from bin.order.order import Orders
from bin.pay.pay import Pay
from bin import config


def register_corps():
    mobile = config.mobile
    for count in range(config.number):
        try:
            start_time = time.time()
            r = Register(str(mobile+count))
            r.add_corp()
        except Exception:
            exstr = traceback.format_exc()
            logging.error(exstr)
        finally:
            end_time = time.time()
            cost_time = end_time - start_time
            logging.warning('cost %d seconds' % cost_time)


def fake_data():
    mobile = config.mobile
    for count in range(config.number):
        try:
            start_time = time.time()
            r = Register(str(mobile+count))
            r.add_corp()
        except Exception:
            exstr = traceback.format_exc()
            logging.error(exstr)
        finally:
            end_time = time.time()
            cost_time = end_time - start_time
            logging.warning('cost %d seconds' % cost_time)

        try:
            start_time = time.time()
            logging.warning('Fake ' + str(mobile+count) + ' datas......')

            logging.warning('Login')
            ydh = Login()
            ydh.login(str(mobile+count), '123456')
            if ydh.login_succeed is not True:
                logging.error('login failed')
                break

            if config.service_type_flag:
                result = r.get_account_type(ydh.get_dbid())
                if int(result[0]) != config.service_type:
                    r.update_service_type(ydh.dbid)
                    logging.warning('update corp %s service type to %d' % (mobile+count, config.service_type))

            if config.setting_flag:
                logging.warning('Update system setting')
                setting_system = SettingSystem(ydh)
                setting_system.update_customer()
                setting_system.update_goods()
                setting_system.update_fund_account()
                setting_system.update_messages_setting()

                logging.warning('Update pay account')
                pay = Pay(ydh)
                pay.save_online_pay_account(1)
                pay.save_online_pay_account(2)
                pay.save_company_bank()

            if config.customer_flag:
                logging.warning('Add departments')
                department = Department(ydh)
                department.init_departments()

                logging.warning('Add levels')
                level = Level(ydh)
                level.init_levels()

                logging.warning('Import customers')
                customers = Customers(ydh)
                customers.init_customers()

            if config.payment_flag:
                logging.warning('Import payment')
                pay = Pay(ydh)
                pay.init_pay()

            if config.goods_flag:
                logging.warning('Add brands')
                brand = Brand(ydh)
                brand.init_brands()

                logging.warning('Add category')
                category = Category(ydh)
                category.init_categories()

                logging.warning('Import goods')
                products = Goods(ydh)
                products.init_goods()

            # if config.supplier_flag:
            #     logging.warning('Add suppliers')
            #     supplier = Supplier(ydh)
            #     supplier.init_suppliers()
            #     supplier.add_supplier_goods()
            #
            # if config.purchase_flag:
            #     logging.warning('Add purchase order')
            #
            # if config.inventory_flag:
            #     logging.warning('Import inventory')
            #     inventory = Inventory(ydh)
            #     inventory.init_inventory()

            if config.order_flag:
                logging.warning('Import orders')
                orders = Orders(ydh)
                orders.init_orders()

            # if config.ad_flag:
            #     logging.warning('Add AD')
            #     ad = Ad(ydh)
            #     ad.init_ad()

            # if config.notification_flag:
            #     logging.warning('Add notification')
            #     notification = Notification(ydh)
            #     notification.init_notification()

            if config.promotion_flag:
                logging.warning('Add promotion')
                promotion = Promotion(ydh)
                promotion.init_promotion()

        except Exception:
            exstr = traceback.format_exc()
            logging.error(exstr)
        finally:
            ydh.get_session().close()
            end_time = time.time()
            cost_time = end_time - start_time
            logging.warning('cost time: %d' % cost_time)


def main():
    if config.backup_flag:
        util.backup_data()

    fake_data()


if __name__ == '__main__':
    main()
