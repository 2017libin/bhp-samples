import socket

def sample_tcp_client():
    dest_host = "www.baidu.com"
    dest_port = 80

    # 创建一个socket对象
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 建立连接
    client.connect((dest_host, dest_port))

    # 发送数据
    client.send(b"GET / HTTP/1.1\r\nHost: baidu.com\r\n\r\n")

    # 接收数据
    response = client.recv(4096)

    print(response.decode())
    client.close()

if __name__ == "__main__":
    sample_tcp_client()