import hashlib
import string
import socket
import base64
import sys
import random

import libnum

chars = '1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'
def brute_crack(suffix:str, hexhash):
    for c1 in chars:
        for c2 in chars:
            for c3 in chars:
                for c4 in chars:
                    data = c1+c2+c3+c4+suffix
                    if hashlib.sha256(data.encode()).hexdigest() == hexhash:
                        return c1+c2+c3+c4

if __name__ == '__main__':
    ip = '172.52.126.72'
    port = 9998
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip,port))
    response = client.recv(4096)
    print(response)

    s = response.decode().split('\n')[0]
    # print(s)

    XXXX = brute_crack(s[12:28], s[33:])
    print(XXXX)
    client.send((XXXX+'\n').encode())
    response = client.recv(4096)
    print(response.decode())

    while True:
        # 不知道到底要猜什么？种子还是随机数？
        predict = (hashlib.sha256((''.join(random.sample(string.ascii_letters + string.digits, 4))+s[12:28]).encode()).hexdigest()+'\n').encode()
        # predict = ((''.join(random.sample(string.ascii_letters + string.digits, 20))) + '\n').encode()
        # print(predict)
        client.send(predict)

        response = client.recv(4096)
        print(response)
    # ans = input()
    # client.send((ans+'\n').encode())