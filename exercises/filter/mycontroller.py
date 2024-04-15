#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep

import grpc

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.switch import ShutdownAllSwitchConnections

def writeForwardingRule(p4info_helper, sw, dst_ip_addr, 
                         dst_eth_addr, port):
    """
    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    :param dst_ip_addr: the destination IP to match
    :param dst_eth_addr: the destination Ethernet address to write in the packet
    :param port: the port to forward the packet out of 
    """
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_exact",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr)
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dst_eth_addr,
            "port": port,
        })
    sw.WriteTableEntry(table_entry)
    print("Installed forwarding rule to %s on %s" % (dst_ip_addr, sw.name))

def writeAllForwardingRules(p4info_helper, sw_list):
    s1, s2, s3, s4 = sw_list

    # Write forwarding rules for s1
    writeForwardingRule(p4info_helper, sw=s1, dst_ip_addr="10.0.1.1", 
                         dst_eth_addr="08:00:00:00:01:11", port=1) 

    writeForwardingRule(p4info_helper, sw=s1, dst_ip_addr="10.0.2.2", 
                         dst_eth_addr="08:00:00:00:02:22", port=2) 

    writeForwardingRule(p4info_helper, sw=s1, dst_ip_addr="10.0.3.3", 
                         dst_eth_addr="08:00:00:00:03:00", port=3) 

    writeForwardingRule(p4info_helper, sw=s1, dst_ip_addr="10.0.4.4", 
                         dst_eth_addr="08:00:00:00:04:00", port=4) 

    # Write forwarding rules for s2
    writeForwardingRule(p4info_helper, sw=s2, dst_ip_addr="10.0.1.1",
                         dst_eth_addr="08:00:00:00:03:00", port = 4)
    
    writeForwardingRule(p4info_helper, sw=s2, dst_ip_addr="10.0.2.2",
                         dst_eth_addr="08:00:00:00:04:00", port = 3) 

    writeForwardingRule(p4info_helper, sw=s2, dst_ip_addr="10.0.3.3",
                         dst_eth_addr="08:00:00:00:03:33", port = 1)

    writeForwardingRule(p4info_helper, sw=s2, dst_ip_addr="10.0.4.4",
                         dst_eth_addr="08:00:00:00:04:44", port = 2)

    # Write forwarding rules for s3
    writeForwardingRule(p4info_helper, sw=s3, dst_ip_addr="10.0.1.1",
                         dst_eth_addr="08:00:00:00:01:00", port = 1)
    
    writeForwardingRule(p4info_helper, sw=s3, dst_ip_addr="10.0.2.2",
                         dst_eth_addr="08:00:00:00:01:00", port = 1) 

    writeForwardingRule(p4info_helper, sw=s3, dst_ip_addr="10.0.3.3",
                         dst_eth_addr="08:00:00:00:02:00", port = 2)

    writeForwardingRule(p4info_helper, sw=s3, dst_ip_addr="10.0.4.4",
                         dst_eth_addr="08:00:00:00:02:00", port = 2)

    # Write forwarding rules for s4
    writeForwardingRule(p4info_helper, sw=s4, dst_ip_addr="10.0.1.1",
                         dst_eth_addr="08:00:00:00:01:00", port = 2)
    
    writeForwardingRule(p4info_helper, sw=s4, dst_ip_addr="10.0.2.2",
                         dst_eth_addr="08:00:00:00:01:00", port = 2) 

    writeForwardingRule(p4info_helper, sw=s4, dst_ip_addr="10.0.3.3",
                         dst_eth_addr="08:00:00:00:02:00", port = 1)

    writeForwardingRule(p4info_helper, sw=s4, dst_ip_addr="10.0.4.4",
                             dst_eth_addr="08:00:00:00:02:00", port = 1)


def writeFilterRule(p4info_helper, sw, src_ip_addr, src_port):
    """
    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    :param src_ip_addr: the source IP to match
    :param src_port: the src UDP port to match
    """

    # TODO: similar to writeForwardingRule,
    #       create a rule to install in the 
    #       filter table that was defined in 
    #       the P4 program. Make sure that the
    #       name of the table, keys, and actions
    #       match what is specified in the P4 
    #       program.
    
    print("Installed filter rule for (%s, %d) on %s" % (src_ip_addr, src_port, sw.name))

def writeAllFilterRules(p4info_helper, sw_list):
    
    # read the susp descriptions from susp.txt
    with open("susp.txt") as fp:
        for line in fp:
            parts = [s.strip() for s in line.strip().split()]
            if len(parts) != 2:
                continue

            (src_ip_addr, src_port) = parts
            try:
                src_port = int(src_port)
            except:
                continue

            for sw in sw_list:
                writeFilterRule(p4info_helper, sw=sw, 
                                src_ip_addr = src_ip_addr, src_port = src_port) 


def printGrpcError(e):
    print("gRPC Error:", e.details(), end=' ')
    status_code = e.code()
    print("(%s)" % status_code.name, end=' ')
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))

def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')

        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')

        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        
        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s2")
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s3")
        
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s4")

        sw_list = [s1, s2, s3, s4]
        # Write forwarding rules
        writeAllForwardingRules(p4info_helper, sw_list);  

        # Write filter rules
        writeAllFilterRules(p4info_helper, sw_list);

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/filter.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/filter.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
