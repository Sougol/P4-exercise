#!/usr/bin/env python3
import random
import socket
import sys

from filter_header import Filter
from scapy.all import IP, UDP, Ether, get_if_hwaddr, get_if_list, sendp


def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():

    if len(sys.argv)<4:
        print('pass 2 arguments: <destination IP> <source port> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    src_port = int(sys.argv[2])
    message = sys.argv[3]
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=addr) / Filter() / UDP(dport=1234, sport=src_port) / message
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
