import configparser


class Config:

    def __init__(self, config_file):
        all_config = configparser.ConfigParser()
        # with open(config_file, 'r', encoding='utf-8') as cfg_file:
        #     all_config.read(cfg_file)          # 注释的写法行不通
        all_config.read(config_file, encoding="utf-8")
        self.db_ip = all_config.get('db', 'ip')

        self.db_user = all_config.get('db', 'user')
        self.db_password = all_config.get('db', 'password')
        self.db_port = int(all_config.get('db', 'port'))

        self.number = int(all_config.get('user', 'number'))
        self.mobile = int(all_config.get('user', 'mobile'))

        self.service_type_flag = int(all_config.get('user', 'service_type_flag'))
        self.service_type = int(all_config.get('user', 'service_type'))

        self.customer_lower_limit = int(all_config.get('threshold', 'customer_lower_limit'))
        self.customer_upper_limit = int(all_config.get('threshold', 'customer_upper_limit'))
        self.customer_department_lower_limit = int(all_config.get('threshold', 'customer_department_lower_limit'))
        self.customer_department_upper_limit = int(all_config.get('threshold', 'customer_department_upper_limit'))
        self.customer_level_lower_limit = int(all_config.get('threshold', 'customer_level_lower_limit'))
        self.customer_level_upper_limit = int(all_config.get('threshold', 'customer_level_upper_limit'))

        self.payment_limit = int(all_config.get('threshold', 'payment_limit'))

        self.goods_category_lower_limit = int(all_config.get('threshold', 'goods_category_lower_limit'))
        self.goods_category_upper_limit = int(all_config.get('threshold', 'goods_category_upper_limit'))
        self.goods_brand_lower_limit = int(all_config.get('threshold', 'goods_brand_lower_limit'))
        self.goods_brand_upper_limit = int(all_config.get('threshold', 'goods_brand_upper_limit'))
        self.goods_lower_limit = int(all_config.get('threshold', 'goods_lower_limit'))
        self.goods_upper_limit = int(all_config.get('threshold', 'goods_upper_limit'))

        self.inventory_limit = int(all_config.get('threshold', 'inventory_limit'))

        self.supplier_lower_limit = int(all_config.get('threshold', 'supplier_lower_limit'))
        self.supplier_upper_limit = int(all_config.get('threshold', 'supplier_upper_limit'))

        self.purchase_order_lower_limit = int(all_config.get('threshold', 'purchase_order_lower_limit'))
        self.purchase_order_upper_limit = int(all_config.get('threshold', 'purchase_order_upper_limit'))

        self.order_file_num = int(all_config.get('threshold', 'order_file_num'))
        self.goods_in_order_num = int(all_config.get('threshold', 'goods_in_order_num'))
        self.order_lower_limit = int(all_config.get('threshold', 'order_lower_limit'))
        self.order_upper_limit = int(all_config.get('threshold', 'order_upper_limit'))

        self.ad_limit = int(all_config.get('threshold', 'ad_limit'))
        self.promotion_limit = int(all_config.get('threshold', 'promotion_limit'))
        self.combined_promotion_limit = int(all_config.get('threshold', 'combined_promotion_limit'))
        self.combined_promotion_product_count = int(all_config.get('threshold', 'combined_promotion_product_num'))
        self.notification_limit = int(all_config.get('threshold', 'notification_limit'))

        self.backup_flag = int(all_config.get('flag', 'backup'))
        self.setting_flag = int(all_config.get('flag', 'setting'))
        self.customer_flag = int(all_config.get('flag', 'customer'))
        self.payment_flag = int(all_config.get('flag', 'payment'))
        self.goods_flag = int(all_config.get('flag', 'goods'))
        self.supplier_flag = int(all_config.get('flag', 'supplier'))
        self.purchase_flag = int(all_config.get('flag', 'purchase'))
        self.inventory_flag = int(all_config.get('flag', 'inventory'))
        self.order_flag = int(all_config.get('flag', 'order'))
        self.ad_flag = int(all_config.get('flag', 'ad'))
        self.promotion_flag = int(all_config.get('flag', 'promotion'))
        self.delete_promotion_flag = int(all_config.get('flag', 'delete_promotion'))
        self.notification_flag = int(all_config.get('flag', 'notification'))

