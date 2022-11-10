import ipaddress
import os
import socket
import struct
import sys
import threading
import time
from tqdm import tqdm
class IP:
    def __init__(self, buff=None):
        # B: byte、H: half world、4s: string with 4 bytes
        header = struct.unpack('<BBHHHBBH4s4s', buff)
        self.ver = header[0] >> 4
        self.ihl = header[0] & 0xf
        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.sum = header[7]
        self.src = header[8]
        self.dst = header[9]

        self.src_ip = ipaddress.ip_address(self.src)
        self.dst_ip = ipaddress.ip_address(self.dst)

        self.protocol_map = {1:'ICMP', 6:'TCP', 17:'UDP'}

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            # print(f'No protocol for protocol_num = {self.protocol_num}')
            print(f'No protocol with number {self.protocol_num}')
            self.protocol = 'DontKnow'

class ICMP:
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]

def udp_sender():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:  # 创建一个UDP socket
        print(f'udp_sender start')
        for ip in tqdm(ipaddress.ip_network(SUBNET).hosts(), total=2**15):
            # print(ip)
            sender.sendto(MESSAGE, (str(ip), 65212))
        print('udp_sender finish')

class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == 'nt':
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)  # 接收
        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)  # 接收完整的ip头
        if os.name == 'nt':
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        hosts_up = set([f'{str(self.host)} *'])
        try:
            while True:
                raw_buff = self.socket.recvfrom(65535)[0]
                ip_header = IP(raw_buff[0:20])

                if ip_header.protocol == 'ICMP':
                    offset = ip_header.ihl * 4
                    buf = raw_buff[offset:offset + 8]
                    icmp_header = ICMP(buf)

                    if icmp_header.code == 3 and icmp_header.type == 3:
                        if ipaddress.ip_address(ip_header.src_ip) in ipaddress.IPv4Network(SUBNET):
                            if raw_buff[len(raw_buff)-len(MESSAGE):] == MESSAGE:
                                tgt = str(ip_header.src_ip)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(tgt)
                                    print(f'Host up: {tgt}')
        except KeyboardInterrupt:
            if os.name == 'nt':
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print(f'User interrupted.')
            if hosts_up:
                print(f'Summary: Hosts up on {SUBNET}')
            for host in sorted(hosts_up):
                print(host)
            sys.exit()

if __name__ == '__main__':
    SUBNET = '10.242.128.0/17'
    MESSAGE = b'PYTHONRULES'

    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '10.242.182.10'
    s = Scanner(host)
    time.sleep(5)
    t = threading.Thread(target=udp_sender())
    t.start()
    s.sniff()