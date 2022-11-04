import socket

def sample_tcp_client():
    dest_host = "0.0.0.0"
    dest_port = 9998

    # 创建一个socket对象
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 建立连接
    client.connect((dest_host, dest_port))

    # 发送数据
    client.send(b"hello")

    # 接收数据
    response = client.recv(4096)

    print(response.decode())
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