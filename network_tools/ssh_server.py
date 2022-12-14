import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __int__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        if (username == 'chase') and (password == '123456'):
            return paramiko.AUTH_SUCCESSFUL

if __name__ == '__main__':
    sever = '0.0.0.0'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((sever, ssh_port))
        sock.listen(100)  #
        print(f'[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print(f'[-] Listen failed:' + str(e))
        sys.exit(1)
    else:
        print('[+] Got a connection!', client, addr)

    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)

    chan = bhSession.accept(20)
    if chan is None:
        print('*** No channel.')
        sys.exit(1)

    print(f'[+] Authenticated!')
    print(chan.recv(1024))
    chan.send('Welcome to bh_ssh'.encode())
    try:
        while True:
            command = input('Enter command: ')
            if command != 'exit':
                chan.send(command.encode())
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit'.encode())
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()

