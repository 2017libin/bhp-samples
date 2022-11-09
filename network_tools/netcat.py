import argparse
import socket
import textwrap
import sys
import threading
import subprocess
import shlex

def execute(cmd: str):
    cmd = cmd.strip()  # 去掉首尾的空白字符
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # socket关闭后端口可立即重用

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    # netcat作为接收方（客户端）
    def send(self):
        self.socket.connect((self.args.target, self.args.port))  # 建立连接
        # if self.buffer:
        #     self.socket.send(self.buffer)  # 发送数据
        try:
            while True:
                response = ''
                while True:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:  # 如果获得响应
                    print(response, end='')
                    buffer = input()
                    buffer += '\n'
                    self.socket.send(buffer.encode())  # 发送数据
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    # netcat作为发送方（服务端）
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))  # 监听端口
        self.socket.listen(5)  # 最大连接数
        while True:
            client_socket, _ = self.socket.accept()  # 返回一个新的套接字用于接收和发送数据
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    # client_socket用来和连接的客户端进行通信
    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Save file {self.args.upload}'
            client_socket.send(message)
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'\nBHP2: #> ')  # 发送命令行提示符
                    while '\n' not in cmd_buffer.decode():  # 接收命令
                        tmp = client_socket.recv(64)
                        print(f"tmp: {tmp}")
                        cmd_buffer += tmp
                    response = execute(cmd_buffer.decode())  # 执行命令
                    if response:
                        print(response)
                        client_socket.send(response.encode())  # 命令的输出不为空，发送命令的输出结果
                    cmd_buffer = b''  # 清空cmd_buffer，准备接收下一次命令
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    example_IP = '192.168.1.1'
    example_PORT = 1234
    parser = argparse.ArgumentParser(
        description='BHP2 Net Tool',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent(f'''Example:
            netcat.py -t {example_IP} -p {example_PORT} -l -c  # command shell
            netcat.py -t {example_IP} -p {example_PORT} -l -u=filename  # upload to file
            netcat.py -t {example_IP} -p {example_PORT} -l -e=\"[cmd command]\"  # execute cmd command
            echo 'hello' | ./netcat.py -t {example_IP} -p {example_PORT}  # echo text to {example_IP}:{example_PORT}
            netcat.py -t {example_IP} -p {example_PORT} # connect to {example_IP}:{example_PORT}
        ''')
    )
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute cmd command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='network port')
    parser.add_argument('-t', '--target', default='0.0.0.0', help='IP address')
    parser.add_argument('-u', '--upload', help='upload file')

    args = parser.parse_args()
    buffer = ''
    # if args.listen:
    #     buffer = ''
    # else:
    #     buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()