import contextlib
import os
import queue
import requests
import sys
import threading
import time


def gather_paths():
    # 打印当前路径下的所有文件
    for root, dirs, files in os.walk("."):
        for name in files:
            if os.path.splitext(name)[1] not in PASSED:
                continue

            path = os.path.join(root, name)
            if path.startswith('.'):
                path = path[1:]
            print(path)
            web_paths.put(path)

# 将生成器函数转换为上下文管理器
@contextlib.contextmanager
def chdir(path):
    # 开始时进入到path中，结束后退回到原来的目录
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        # yield返回的变量放在as后的变量中
        yield  # 带有yield的函数是一个生成器，具体参考网上教程
    finally:
        os.chdir(this_dir)

def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = f'{TARGET}{path}'
        time.sleep(2)
        r = requests.get(url)
        if r.status_code == 200:
            answers.put(url)
            print('+')
        else:
            print('-')

def run():
    mythreads = list()
    for i in range(THREADS):
        print(f'Spawning thread {i}')
        t = threading.Thread(target=test_remote)
        mythreads.append(t)

    for thread in mythreads:
        thread.join()

if __name__ == '__main__':
    FILTERED = ['.jpg', '.gif', '.png', '.css']
    PASSED = ['.txt', '.php']
    TARGET = 'xxx'
    THREADS = 10

    answers = queue.Queue()
    web_paths = queue.Queue()

    with chdir('/mnt/d/WordPress-master'):
        print(os.getcwd())
        gather_paths()
    # with结束回到原来的路径
    run()

    with open('myansers.txt', 'w') as f:
        while not answers.empty():
            f.write(f'{answers.get()}\n')
    print('done')