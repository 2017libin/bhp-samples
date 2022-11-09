import paramiko

def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.realines() + stderr.readlines()
    if output:
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    import getpass
    user = input('Username:')
    password = getpass.getpass()
    ip = input('Enter server IP or <CR>: ') or '0.0.0.0'
    port = input('Enter port or <CR>: ') or '22'
    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)