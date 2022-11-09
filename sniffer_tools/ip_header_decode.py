import ipaddress
import os
import socket
import struct
import sys

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
            sys.exit(1)
            pass

def sniff(host):
    name = os.name
    if name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            raw_buff = sniffer.recvfrom(65535)[0]
            ip_header = IP(raw_buff[0:20])

            # print(f'{ip_header.protocol}: {ip_header.src_ip}->{ip_header.dst_ip}')
            print(ip_header.protocol, ip_header.src_ip, ip_header.dst_ip)
    except KeyboardInterrupt:
        if name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '10.255.124.73'
    sniff(host)