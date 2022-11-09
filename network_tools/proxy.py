import sys
import socket
import threading

# 不可打印的字符包括有ascii未定义的字符, 换行符等
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

def proxy_handler(local_socket:socket, remote_host:str, remote_port:int, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print(f'[<==] Sending {len(remote_buffer)} bytes to localhost.')
        local_socket.send(remote_buffer)

    while True:
        # localhost -> remote
        locale_buffer = receive_from(local_socket)
        if len(locale_buffer):
            line = f'[==>]Received {len(locale_buffer)} bytes from localhost.'
            print(line)
            hexdump(locale_buffer)

            locale_buffer = request_handler(locale_buffer)
            remote_socket.send(locale_buffer)
            print(f'[==>]Sent to remote.')

        # remote -> localhost
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            line = f'[<==]Received {len(remote_buffer)} bytes from remote.'
            print(line)
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            local_socket.send(remote_buffer)
            print(f'[<==]Sent to localhost.')

        if not len(locale_buffer) or not len(remote_buffer):
            local_socket.close()
            remote_socket.close()
            print(f'[*] No more data. Closing connections.')
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f'problem on bind: {e}')
        sys.exit(0)

    print(f'[*] Listening to listen on {local_host}:{local_port}')
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        print(f'> Received incoming connection from {addr[0]}:{addr[1]}')
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    server_loop(local_host, local_port, remote_host, remote_port, True)

if __name__ == '__main__':
    main()