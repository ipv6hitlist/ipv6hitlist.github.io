import argparse
import ipaddress
import lzma, os, tqdm
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("linecount", type=int, help="Amount of seed addresses")
parser.add_argument("--num-workers", type=int, default=24, dest="num_workers")
args = parser.parse_args()

panzer = lambda m, k: m + (m / k) - 1

NUM_WORKERS = args.num_workers
# These parameters can be adjusted
THRESHOLD_SIZE = 100
THRESHOLD_DISTANCE = 64
THRESHOLD_GROUP = 10
_, fn = os.path.split(args.input)

# Returns all IP addresses between ip1 and ip2
def ip_interpol(ip1, ip2):
    ipi1 = int.from_bytes(ipaddress.ip_address(ip1).packed, "big") + 1
    ipi2 = int.from_bytes(ipaddress.ip_address(ip2).packed, "big")
    return [str(ipaddress.IPv6Address(ip)) for ip in range(ipi1, ipi2)]

# Returns the byte distance between two IP addresses
def ip_dist(ip1, ip2):
    ipi1 = int.from_bytes(ipaddress.ip_address(ip1).packed, "big")
    ipi2 = int.from_bytes(ipaddress.ip_address(ip2).packed, "big")
    return ipi2 - ipi1

def work(idx):
    with open(args.input, "r") as f:
        chain_start = None
        ip_prev = None
        ip_chain = 0
        results = []
        result_ips = []
        next(f)
        
        if idx == 0:
            tq = tqdm.tqdm(total=args.linecount)

        start = int(args.linecount * (idx / NUM_WORKERS))
        end = int(args.linecount * ((idx + 1) / NUM_WORKERS))
        skip = True
        for i, line in enumerate(f):
            if idx == 0:
                tq.update()

                if skip and i >= end:
                    continue

            if i < start - 1:
                continue

            ip = line.strip()

            if i == start - 1 or (idx == 0 and i == 0):
                ip_prev = ip
                chain_start = ip
                continue

            dist = ip_dist(ip_prev, ip)

            if skip and dist <= THRESHOLD_DISTANCE:
                continue

            skip = False

            # Include addresses with higher distance if a higher amount
            # addresses is already in this cluster. Probability is calculated
            # with the German Tank Problem estimator
            panzer_dist = panzer(ip_dist(chain_start, ip), ip_chain) if ip_chain else dist
            if (not dist <= THRESHOLD_DISTANCE) and (not panzer_dist <= THRESHOLD_DISTANCE):
                if ip_chain > THRESHOLD_GROUP:
                    results.append(f"{chain_start},{ip_chain},{ip_prev}\n")
                
                if i >= end:
                    skip = True
                    if idx > 0:
                        return results, result_ips

                ip_chain = 0
                chain_start = ip
            else:
                if ip_prev:
                    result_ips += ip_interpol(ip_prev, ip)
                ip_chain += 1
            
            ip_prev = ip

        return results, result_ips

with multiprocessing.Pool(NUM_WORKERS) as p:
    idx = list(range(NUM_WORKERS))
    res = p.map(work, idx)
    with open(fn + ".chains", "w") as fw, open(fn + ".chainips", "w") as fi:
        for l, li in res:
            for el in l:
                fw.write(el)
            for el in li:
                fi.write(el + "\n")
