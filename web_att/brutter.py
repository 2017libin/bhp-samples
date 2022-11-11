import queue
import requests
import threading
import sys

AGENT = ''
EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
TARGET = 'http://testphp.vulnweb.com'
THREADS = 50
WORDLIST = './all.txt'

def get_words(resume=None):
    def extend_words(word):
        if '.' in word:
            words.put(f'/{word}')
        else:
            words.put(f'/{word}/')
        for ext in EXTENSIONS:
            words.put(f'/{word}{ext}')
    with open(WORDLIST) as f:
        raw_words = f.read()

    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():
        if found_resume:
            extend_words(word)
        elif word == resume:
            found_resume = True
            print(f'Resuming wordlist from: {word}')
        else:
            # print(word)
            extend_words(word)
    return words

def dir_bruter(words):
    headers = {'User-Agent': AGENT}
    while not words.empty():
        url = f'{TARGET}{words.get()}'
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            sys.stderr.write('x')  # 重定向到错误输出
            sys.stderr.flush()
            continue
        if r.status_code == 200:
            print(f'Success ({r.status_code}: {url})')
        elif r.status_code == 404:
            sys.stderr.write('.')  # 重定向到错误输出
            sys.stderr.flush()
        else:
            print(f'Others ({r.status_code}: {url})')

if __name__ == '__main__':
    words = get_words()
    input('Press return to continue.')
    for _ in range(THREADS):
        t = threading.Thread(target=dir_bruter, args=(words,))
        t.start()