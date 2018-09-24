#!/usr/bin/env python3

import argparse
import SubnetTree

def read_nondense(tree, fname):
    return fill_tree(tree, fname, ",0")

def read_dense(tree, fname):
    return fill_tree(tree, fname, ",1")

def fill_tree(tree, fname, suffix):
    with open(fname) as fh:
        for line in fh:
            line = line.strip()
            tree[line] = line + suffix
    return tree


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-dpd-dir", required=True, help="Directory with DPD output files")
    parser.add_argument("-d", "--date", required=True, help="Date and time in YYYY-MM-DD-HHMM of input files")
    parser.add_argument("-f", "--target-file", required=True, help="Target file for which lookup should be performed")
    args = parser.parse_args()

    # Store dense and non-dense prefixes in a single subnet tree
    tree = SubnetTree.SubnetTree()


    # Read prefix-based DPD results
    # 2018-04-25-2300.csv.dpdprefix.pfxonly.sortu.dense
    # 2018-04-25-2300.csv.dpdprefix.pfxonly.sortu.nondense
    tree = read_dense(tree, args.input_dpd_dir + "/" + args.date + ".csv.dpdprefix.pfxonly.sortu.dense")
    tree = read_nondense(tree, args.input_dpd_dir + "/" + args.date + ".csv.dpdprefix.pfxonly.sortu.nondense")

    # Read target-based DPD results
    # 2018-04-25-2300.csv.dpdtarget.slash100.threshold.pfxonly.randomips.pfxonly.sortu.dense
    # 2018-04-25-2300.csv.dpdtarget.slash100.threshold.pfxonly.randomips.pfxonly.sortu.nondense
    for i in range(64, 125, 4):
        tree = read_dense(tree, args.input_dpd_dir + "/" + args.date + ".csv.dpdtarget.slash" + str(i) + ".threshold.pfxonly.randomips.pfxonly.sortu.dense")
        tree = read_nondense(tree, args.input_dpd_dir + "/" + args.date + ".csv.dpdtarget.slash" + str(i) + ".threshold.pfxonly.randomips.pfxonly.sortu.nondense")


    # Read targets, find longest prefix and print output
    with open(args.target_file) as fh:
        for line in fh:
            line = line.strip()
            print(line + "," + tree[line])

if __name__ == "__main__":
    main()
