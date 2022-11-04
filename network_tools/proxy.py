import sys
import socket
import threading

# 不可打印的字符包括有ascii未定义的字符、换行符等
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])  # [exp] and A or B

# 打印字符串
def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        hexa = ''.join([f'{ord(c):02x} ' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
        if show:
            for line in results:
                print(line)
        else:
            return results

# 接收数据
def receive_from(connection):
    buffer = b''
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception:
        pass
    return buffer

# 请求数据包处理函数
def request_handler(buffer):
    return buffer

# 响应数据包处理函数
def response_handler(buffer):
    return buffer

def proxy_handler(client_socket:socket, remote_host:str, remote_port:int, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_host)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print(f'[<==] Sending {len(remote_buffer)} bytes to localhost.')
        client_socket
if __name__ == '__main__':
    hexdump('python \n hell \t jijl \t\t\t\t jijoi')