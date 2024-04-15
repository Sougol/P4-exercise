#!/usr/bin/env python3
import os
import sys
import signal

from filter_header import *
from scapy.all import IP, ICMP, UDP, get_if_list, sniff

fout = None

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def handle_pkt(pkt):
    global fout
    if not ICMP in pkt and IP in pkt:
        if pkt[IP].proto == PROTO_FILTER and Filter in pkt:
            if pkt[Filter].proto == PROTO_UDP and UDP in pkt:
                srcip = pkt[IP].src
                srcport = pkt[UDP].sport
                payload_str = pkt[UDP].payload.load
                pkt_id = int(payload_str)
                is_susp = False if pkt[Filter].susp == 0 else True 
                fout.write(f'{pkt_id} {srcip} {srcport} {is_susp}\n')
                fout.flush()
                pkt.show()
                sys.stdout.flush()

def cleanup():
    global fout
    fout.close()

def main(fout_path):
    global fout
    fout = open(fout_path, 'w')
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(iface = iface,
          lfilter=lambda pkt: pkt[Ether].src != Ether().src,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("pass one argument: <output file>")
        exit(1)
 
    fout_path = sys.argv[1]     
    main(fout_path)
