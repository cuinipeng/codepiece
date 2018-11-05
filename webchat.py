#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=no-member
import os
import os.path
import re
import time
import requests
import urllib.parse
from lxml import etree
HTTP_OK = requests.codes.ok

'''
GET https://wx.qq.com/
    Host: wx.qq.com

GET https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage&fun=new&lang=en_US&_=1537188851290

GET https://login.weixin.qq.com/qrcode/obuic3io1Q==
    Accept: */*
    Accept-Encoding: gzip, deflate, br
    Accept-Language: en-US,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.5,zh-HK;q=0.3,en;q=0.2
    Cache-Control: no-cache
    Connection: keep-alive
    Host: login.weixin.qq.com
    Pragma: no-cache
    Referer: https://wx.qq.com/
    User-Agent: Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/62.0

GET https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=ocQAh0BCRw==&tip=0&r=408598194&_=1537189542508

GET https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=ocQAh0BCRw==&tip=0&r=408623309&_=1537189542507

    window.code=408;

    window.code=200;
    window.redirect_uri="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=A596T36z8AHoc-15VuPR6Gz4@qrticket_0&uuid=ocQAh0BCRw==&lang=en_US&scan=1537189704";
'''

class CustomAuth(requests.auth.AuthBase):
    def __init__(self, username):
        self._username = username

    def __call__(self, req):
        req.headers['Custom-Header'] = self._username
        return req


class WebChat(object):
    '''
    Login webchat and get user list
    '''
    qrcode_uuid_url = 'https://login.wx.qq.com/jslogin'
    qrcode_qs_redirect_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage'
    qrcode_base_url = 'https://login.weixin.qq.com/qrcode/'
    login_url = None
    web_wx_init_url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit'

    def __init__(self):
        self._session = requests.session()
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
            "Host": "https://wx.qq.com/",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive"
        }
        self._proxies = {
            'http:': 'http://user:pass@host:port/',
            'https:': 'http://user:pass@host:port/',
            'no_proxy': 'localhost,127.0.0.1'
        }
        self._session.headers.update(self._headers)
        # self._session.auth = ('user', 'pass')
        # self._session.proxies = self._proxies
        self._qrcode_uuid = None
    
    def set_session_host_header(self, url):
        host = urllib.parse.urlparse(url).netloc
        self._session.headers.update({'Host': host})

    def get_qrcode_url(self):
        url = self.qrcode_uuid_url
        # query string
        payload = {
            'appid': 'wx782c26e4c19acffb',
            'redirect_uri': self.qrcode_qs_redirect_url,
            'fun': 'new',
            'lang': 'en_US',
            '_': str(int(time.time() * 1000))
        }
        self.set_session_host_header(url)
        r = self._session.get(url, params=payload)
        if r.status_code != HTTP_OK:
            r.raise_for_status()
            return None
        
        pattern = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
        match = re.search(pattern, r.text)

        if match.group(1) != '200':
            return None

        self._qrcode_uuid = match.group(2)
        return self.qrcode_base_url + match.group(2)

    def download_qrcode(self, qrcode_url):
        url = qrcode_url
        self.set_session_host_header(url)
        r = self._session.get(url)
        if r.status_code != HTTP_OK:
            r.raise_for_status()
            return None
        
        suffix = r.headers.get('Content-Type').split('/')[-1]
        filename = 'webchat_qrcode.' + suffix
        with open(filename, 'wb') as fd:
            fd.write(r.content)

        return filename

    def open_qrcode_for_scan(self, filename):
        # Windows System
        if not os.path.exists(filename):
            return
        
        os.startfile(filename)

    def check_login_status(self, max_check_times=16):
        # Check login status until the user scan qrcode
        cnt = 0
        login_status = False
        while True:
            print('[%d] checking webchat login status...' % cnt)
            url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login'
            # loginicon = true & uuid = ocQAh0BCRw == &tip = 0 & r = 408623309 & _ = 153718954250
            payload = {
                'loginicon': 'true',
                'uuid': self._qrcode_uuid,
                'tip': 0,
                '_': str(int(time.time() * 1000))
            }
            self.set_session_host_header(url)
            r = self._session.get(url, params=payload)
            if r.status_code != HTTP_OK:
                r.raise_for_status()
                login_status = False
                return login_status
            
            pattern = r'window.code=(\d+);'
            match = re.search(pattern, r.text)
            login_code = match.group(1)
            if login_code == '408':
                # Timeout
                pass
            elif login_code == '201':
                # Scanned
                pass
            elif login_code == '200':
                # Logined
                login_status = True
                'window.redirect_uri="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=A596T36z8AHoc-15VuPR6Gz4@qrticket_0&uuid=ocQAh0BCRw==&lang=en_US&scan=1537189704";'
                pattern = r'window.redirect_uri="(\S+?)";'
                match = re.search(pattern, r.text)
                self.login_url = match.group(1)
                break
            
            cnt += 1
            if cnt == max_check_times:
                login_status = False
                break

            time.sleep(1)

        return login_status

    def login(self):
        url = self.login_url
        if not url:
            return False
        
        print('login redirect url: ' + url)
        self.set_session_host_header(url)
        r = self._session.get(url)
        if r.status_code != HTTP_OK:
            r.raise_for_status()
            return False
        
        url = self.web_wx_init_url
        cookies = self._session.cookies
        payload = {
            'BaseReques': {
                'DeviceID':	'e952785118783101',
                'Sid':	cookies.get('wxsid'),
                'Skey': '',
                'Uin':	cookies.get('wxuin')
            }
        }
        self.set_session_host_header(url)
        url = url + '?r=403695240'
        r = self._session.post(url,  data=payload)
        if r.status_code != HTTP_OK:
            r.raise_for_status()
            return False
        
        print(r.text)
        
    def run(self):
        qrcode_url = self.get_qrcode_url()
        print('qrcode url: ' + qrcode_url)
        qrcode_filename = self.download_qrcode(qrcode_url)
        print('qrcode filename: ' + qrcode_filename)
        self.open_qrcode_for_scan(qrcode_filename)
        login_status = self.check_login_status()
        if not login_status:
            print('webchat login failed')
        self.login()

    def upload_file(self, filename):
        if not os.path.exists(filename):
            return

        url = ''
        files = {
            'file': (filename, open(filename, 'rb'), 'application/zip', {'Expires': 0})
        }
        r = self._session.post(url, files=files)
        r.status_code

    def show(self):
        print(self._session)
        # print(dir(self._session))
        print(self._session.headers)


if __name__ == '__main__':
    webchat = WebChat()
    webchat.run()
