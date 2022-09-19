import argparse
import ipaddress
import lzma, os, tqdm
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("linecount", type=int) # 109795697
parser.add_argument("--num-workers", type=int, default=24, dest="num_workers")
args = parser.parse_args()

NUM_WORKERS = args.num_workers
_, fn = os.path.split(args.input)

def ip_dist(ip1, ip2):
    ipi1 = int.from_bytes(ipaddress.ip_address(ip1).packed, "big")
    ipi2 = int.from_bytes(ipaddress.ip_address(ip2).packed, "big")
    return ipi2 - ipi1

def work(idx, dist_thresh):
    with open(args.input, "r") as f:
        ip_prev = None
        clust_lens = dict()
        clust_len = 0
        
        if idx == 0:
            tq = tqdm.tqdm(total=args.linecount)

        start = int(args.linecount * (idx / NUM_WORKERS))
        end = int(args.linecount * ((idx + 1) / NUM_WORKERS))
        for i, line in enumerate(f):
            if idx == 0:
                tq.update()

                if i >= end:
                    continue
            elif i >= end:
                return clust_lens

            if i < start - 1:
                continue

            ip = line.strip()
            if i == start - 1 or (idx == 0 and i == 0):
                ip_prev = ip
                continue

            dist = ip_dist(ip_prev, ip)
            if dist > dist_thresh:
                if clust_len > 0:
                    if not clust_len in clust_lens:
                        clust_lens[clust_len] = 0
                    clust_lens[clust_len] += 1
                clust_len = 0
            else:
                clust_len += 1
            ip_prev = ip

        return clust_lens

with multiprocessing.Pool(NUM_WORKERS) as p:
    open(fn + ".distances", "w")
    for i in range(1, 11):
        thresh = 2 ** i

        idx = list(zip(range(NUM_WORKERS), [thresh for _ in range(NUM_WORKERS)]))
        res = p.starmap(work, idx)
        data = dict()
        for d in res:
            for key, val in d.items():
                if key in data:
                    data[key] += val
                else:
                    data[key] = val

        with open(fn + ".distances", "a") as fw:
            for key, val in sorted(data.items()):
                fw.write(f"{thresh},{key},{val}\n")