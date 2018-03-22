import requests
from requests import adapters


class Login:

    def __init__(self):
        self.cookies = None
        self.dbid = None
        self.mobile = None
        self.username = None
        self.s = requests.session()
        a = adapters.HTTPAdapter(pool_maxsize=1000)
        self.s.mount('http://', a)
        self.s.mount('https://', a)
        self.login_succeed = False

    def authentication(self, username, password='123456'):
        url = 'https://sso.dinghuo123.com/authentication'
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        data = {'service': '', 'relayState': '',
                'username': username, 'password': password, 'verfCode': ''}
        r = self.s.post(url, headers=headers, data=data)
        authentication_status = r.text[0:2]
        if authentication_status == 'OK':
            return r.text[3:]
        else:
            print('[ERROR Login] %s authentication failed' % username)
            return False

    def login(self, username, password):
        lt = self.authentication(username, password)
        if lt is False:
            return False
        s = self.s
        url = 'https://sso.dinghuo123.com/login'
        data = {'remember_me': 'on', 'relayState': '',
                'username': username, 'password': password,
                'verifyCode': '', 'lt': lt, 'service': ''}
        r = s.post(url, data=data, allow_redirects=True)
        if r.request.url == 'https://sso.dinghuo123.com/accountList?client=web':   # 多打一个斜杠/  ：'https://sso.dinghuo123.com//accountList?client=web':
            user_account_name = r.text.split('<a class="ui-btn ui-btn-theme btn-bindOk" href="/accountList?action=entry&userAccountName=')[-1].split('&serviceName=ydh-web')[0]
            r = s.get('https://sso.dinghuo123.com/accountList?action=entry&userAccountName=%s&serviceName=ydh-web' % user_account_name)

        cookies = {}
        for item in r.request.headers['cookie'].split(';'):
            if item.find('ydhSession') != -1:
                cookies.update({'ydhSession': item.split('=')[1].strip()})
            if item.find('JSESSIONID') != -1:
                cookies.update({'JSESSIONID': item.split('=')[1].strip()})
        if cookies.get('ydhSession') or cookies.get('JSESSIONID'):
            self.mobile = username
            self.cookies = cookies
            self.login_succeed = True
        else:
            print("logging error")
        if r.text.find('dbid') != -1:
            self.dbid = r.text.split("dbid':'")[1].split("',")[0]
        else:
            r = s.get('http://corp.dinghuo123.com/runtime/config')
            self.dbid = str(r.json()['data']['company']['dbid'])
            self.username = str(r.json()['data']['company']['userName'])

    def get_username(self):
        return self.username

    def get_session(self):
        return self.s

    def get_dbid(self):
        return self.dbid

    def get_cookies(self):
        return self.cookies

if __name__ == '__main__':
    ydh = Login()
    ydh.login('18681558460', '111111')    # 只能是绑定一个账号的手机号,不能开代理
    print(ydh.get_cookies())
    print(ydh.get_dbid())
    print(ydh.get_username())

