import logging

from bin.common.login import Login


class RunTimeConfig:

    def __init__(self,ydh):
        self.s = ydh.get_session()
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.file_token = None
        self.get_runtime_config()

    def get_runtime_config(self):
        url = 'http://corp.dinghuo123.com/runtime/config'
        r = self.s.get(url)
        response = r.json()
        if response['code'] == 200:
            self.file_token = response['data']['file_token']
        else:
            logging.error('get runtime file_token failed')
            logging.error(r.text)


if __name__ == '__main__':
    ydh = Login()
    ydh.login('11299996612', '123456')
    runtime_config = RunTimeConfig(ydh)
    logging.info(runtime_config.file_token)