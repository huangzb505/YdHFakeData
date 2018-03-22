import requests
import logging
import pymysql
from bin import config


class Register:

    def __init__(self, mobile):
        self.s = requests.Session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.mobile = mobile

    def check_mobile(self):
        url = 'https://sso.dinghuo123.com/ajaxChecking?action=checkUserNameExist'
        data = {'username': self.mobile}
        r = self.s.post(url, headers=self.headers, data=data)
        if 'ok' in r.json()['data'].keys():
            return True
        else:
            return False

    def add_corp(self):
        if self.check_mobile() is False:
            logging.error('mobile {} have been registered'.format(self.mobile))
            return
        self.s.get('https://sso.dinghuo123.com/apply/apply2')

        url = 'https://sso.dinghuo123.com/register'

        data = {'userName': self.mobile,
                'openId': '',
                'businessTypeId': '1',
                'sc': '',
                'companyName': 'test@dinghuo123.com',
                'bdReg': 'true',
                'linkman': u'铱云测试部',
                'recommendCode': '',
                'source': '0',
                'action': 'ajaxReg',
                'password': '123456',
                'email': ''}

        r = self.s.post(url, data=data)
        res = r.json()
        if res['code'] == 200:
            logging.warning('add corp {} success'.format(self.mobile))
            self.update_service_type(config.service_type)
            logging.warning('update corp {0} service type to {1}'.format(self.mobile, config.service_type))
        else:
            logging.error('add corp {0} failed'.format(self.mobile))
            logging.error(r.text)

    @staticmethod
    def update_service_type(dbid):
        db = pymysql.Connection(config.db_ip, config.db_user, config.db_password, port=config.db_port)
        sql = 'UPDATE platform.`t_service_instance` SET fserviceTypeId={0}, fisPaid=1, ftotalUserNum=100000 WHERE fid={1}'.format(config.service_type, dbid)

        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            logging.error(str(e))
            db.rollback()
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_account_type(dbid):
        db = pymysql.connections(config.db_ip, config.db_user, config.db_password, port=config.db_port)
        sql = 'SELECT FserviceTypeId, fisPaid, ftotalUserNum from platform.`t_service_instance` WHERE fid={}'.format(dbid)

        cursor = db.cursor()
        result = None
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
        except Exception as e:
            logging.error(str(e))
            db.rollback()
        finally:
            cursor.close()
            db.close()
            return result[0]

if __name__ == '__main__':
    new_mobile = '11299996613'
    r = Register(new_mobile)
    r.add_corp()