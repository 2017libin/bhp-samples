import socket
import sys

# Qx:11434785965672261589606890199535869706128834919066537753255291357295335883386744993545133914859016007882335995318431
# Qy:30465948528885354231939070682565909545934318068008494960321220386288581905252659345475703670574526032296727855881964
# flag: kmnO0pk5WzCcPpP+kPhtfCxWXLKQo+oWIbjSZLG0EsGqhwKu8S32D9Gp6DaCVobA

def sample_tcp_client():
    dest_host = "172.52.126.157"
    dest_port = 10002

    # 创建一个socket对象
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 建立连接
    client.connect((dest_host, dest_port))

    # 发送数据
    # client.send(b"1")

    # G = dQ
    # 30899759106379857482354028371747730461531330926446107685011508347435179052171050476289419813436292019778562940121794,
    # 21393750857903822825641654537596970786713122236063014317647096026663428086177137176504348382952072108979062701448466)

    def get_xy(list_byte):
        index1 = list_byte.find('(')
        index2 = list_byte.find(')')
        return (list_byte[index1+1:index2]).split(', ')

    # 输出公钥
    response = client.recv(4096)
    print(response.decode())
    x,y = get_xy(response.decode())
    print(f'Qx:{x}\nQy:{y}')

    # 获取加密后的flag
    client.send(b'2\n')
    response = client.recv(4096)
    print(response.decode())

    # 碰撞kk
    r_list = []
    s_list = []
    msg_list = []
    count = 0
    while True:
        if count % 100 == 0:
            print(count)

        client.send(b'1\n')

        response = client.recv(4096)

        count += 1
        msg = str(count)
        client.send((msg+'\n').encode())

        response = client.recv(4096)
        x,y = get_xy(response.decode())

        if x not in r_list:
            r_list.append(x)
            s_list.append(y)
            msg_list.append(msg)
        else:
            print('find same r with different msg!')
            index = r_list.index(x)
            print(f'm1:{msg_list[index]}')
            print(f'r1:{r_list[index]}\ns1:{s_list[index]}')
            print(f'm2:{msg}')
            print(f'r2:{x}\ns2:{y}')
            break
    client.close()

def sample_udp_client():
    dest_host = "127.0.0.1"
    dest_port = 9997

    # 创建一个socket对象
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 发送数据，不需要建立连接
    client.sendto(b"HELLO", (dest_host, dest_port))

    # 接收数据
    data, addr = client.recvfrom(4096)

    print(data.decode())
    client.close()

if __name__ == "__main__":
    sample_tcp_client()