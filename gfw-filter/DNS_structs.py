import ipaddress
from meta_structs import *

def format_ip(x):
    try:
        return str(ipaddress.ip_address(x))
    except:
        return x

def format_flags(data):
    ret = [data]
    ret.append(f"RCODE - {data & 0xf}")
    data = data >> 4
    for key in ["Non-auth", "Authenticated", "RES", "RA", "RD", "TC", "AA"]:
        ret.append(f"{key} - {data & 0x1}")
        data = data >> 1
    ret.append(f"OPCODE - {data & 0xf}")
    data = data >> 4
    ret.append(f"QR - {data & 0x1}")

    return ret

dns_rr_types = {
    1: "A",
    2: "NS",
    5: "CNAME",
    6: "SOA",
    12: "PTR",
    15: "MX",
    16: "TXT",
    28: "AAAA",
}

query_section = Header("Query Section", [
    TerminatedField("QName", b"\x00"),
    Field("QType", ">H", 2),
    Field("QClass", ">H", 2),
])

rr_format = VariableLengthHeader("Resource Record", [
    Field("Pointer", ">H", 2, hex),
    Field("Type", ">H", 2, print_fmt=lookup_format(dns_rr_types)),
    Field("Class", ">H", 2),
    Field("TTL", ">I", 4),
    Field("Data Length", ">H", 2),
    Field("Data", "", 0, format_ip)
], {
    4:5
})

DNSHeader = RepeatedFieldHeader("DNS Header", [
    Field("Transaction ID", ">H", 2),
    Field("Flags", ">H", 2, print_fmt=format_flags),
    Field("QDCount", ">H", 2),
    Field("ANCount", ">H", 2),
    Field("NSCount", ">H", 2),
    Field("ARCount", ">H", 2),
    query_section,
    rr_format,
    rr_format,
    rr_format
], {
    2: 6,
    3: 7,
    4: 8,
    5: 9
})