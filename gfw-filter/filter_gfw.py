import argparse
import binascii
import ipaddress
import sys
from DNS_structs import DNSHeader

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str)
parser.add_argument("--inverse", action="store_true", default=False)
parser.add_argument("--fulloutput", action="store_true", default=False)
parser.add_argument("--stdin", action="store_true", default=False)
args = parser.parse_args()

lines, error, teredo, okay = 0, 0, 0, 0

if args.stdin:
    f = sys.stdin
else:
    f = open(args.input)

for line in f:
    if lines == 0 and args.fulloutput:
        print(line.strip())
    data = line.split(",")[-2] # get data hexdump
    ip_resolver = line.split(",")[0] # get IP address of resolver
    lines += 1

    try:
        (_, data_unpack), _ = DNSHeader.unpack(binascii.unhexlify(data))
    except:
        error += 1
        continue

    an_count = data_unpack[3][1] # read the amount of RRs in the answer section
    answers = [data_unpack[7 + i][1] for i in range(an_count)] # read all RRs in answer section
    for ans in answers: # iterate over RRs
        if ans[1][1] == 1 or ans[1][1] == 28: # check if address is either IPv4 or IPv6
            ip = ipaddress.ip_address(ans[5][1])
            if ip.version == 6 and ip.teredo: # if IPv6 check if it is a teredo address
                if not args.inverse:
                    if args.fulloutput:
                        print(line.strip())
                    else:
                        print(ip_resolver)
                teredo += 1
                break
    else: # no teredo addresses were found here
        if args.inverse:
            if args.fulloutput:
                print(line.strip())
            else:
                print(ip_resolver)
        okay += 1

if not args.stdin:
    f.close()

#print("Amount of scanned addresses:", lines, file=sys.stderr)
#print("Amount of malformed responses:", error, file=sys.stderr)
#print("Amount of teredo responses:", teredo, file=sys.stderr)
#print("Amount of non-teredo responses:", okay, file=sys.stderr)
