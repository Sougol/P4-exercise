

from scapy.all import *

PROTO_FILTER = 146
PROTO_UDP = 17

class Filter(Packet):
    name = "Filter"
    fields_desc = [
        ByteField("susp", 0),
        ByteField("proto", 0)
    ]
    def mysummary(self):
        return self.sprintf("susp=%susp%, proto=%proto%")


bind_layers(IP, Filter, proto=PROTO_FILTER)
bind_layers(Filter, UDP, proto=PROTO_UDP)

