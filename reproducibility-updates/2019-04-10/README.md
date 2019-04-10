# Reproducibility instructions

This Readme describes the steps to reproduce the results of the IMC'18 paper "Clusters in the Expanse: Understanding and Unbiasing IPv6 Hitlists".

Analysis scripts can be found in the `analysis/` subfolder, data can be found in the `data/` subfolder.


## Ongoing development

While this is the primary data storage, it is frozen with publication.
Future annotations or further explanations will be published at:

https://ipv6hitlist.github.io/

### Update on 2019-04-10

* We updated the `README.md` file to include more detailed setup instructions and to add detailed descriptions of all published data files. The updated version can be found [here](https://ipv6hitlist.github.io/reproducibility-updates/2019-04-10/README.md).
* We fixed the `analysis/jupyter/requirements.txt` file to workaround a bug on older Debian/Ubuntu installations. The updated version can be found [here](https://ipv6hitlist.github.io/reproducibility-updates/2019-04-10/analysis/jupyter/requirements.txt).
* We updated the `checksums.sha512` file to reflect updated checksums for the `README.md` and `analysis/jupyter/requirements.txt` files. The updated version can be found [here](https://ipv6hitlist.github.io/reproducibility-updates/2019-04-10/checksums.sha512).


## Reproduction steps

1. Check downloaded files and extract them: `./check_and_unpack.sh`
2. Change to analysis subfolder: `cd analysis`
3. Run Jupyter notebooks to reproduce the analysis results: `jupyter notebook`


## Analysis

The following analysis scripts can be found in the `analysis/` subfolder.
The analysis is done using [Jupyter Notebook](https://jupyter.org/).

Before you install Jupyter Notebook, make sure that the following packages are installed on your system:

* build-essential
* python3-dev
* python3-venv (optional, only needed if the Python packages should be installed within a Python virtual environment.

The needed Python modules are located in `jupyter/requirements.txt` and can be directly installed in a virtual environment using `pip install -r jupyter/requirements.txt`.

To run the Jupyter notebooks, run `jupyter notebook` in the `analysis/` subfolder.


### Section 3: IPv6 Hitlist Sources

The results from the IPv6 Hitlist Sources analysis (Section 3 in the paper) can be reproduced by running the following notebook:

* `sources-analysis.ipynb`


### Section 4: Entropy Clustering

The results from the Entropy Clustering analysis (Section 4 in the paper) can be reproduced by running the following notebook:

* `entropy-clustering.ipynb`


### Section 5: Aliased Prefix Detection

The results from the Aliased Prefix Detection analysis (Section 5 in the paper) can be reproduced by running the following notebook:

* `apd-analysis.ipynb`


### Section 6: Address Probing

The results from the Address Probing analysis (Section 6 in the paper) can be reproduced by running the following notebook:

* `probing-analysis.ipynb`


### Section 7: Learning New Addresses

The results from the Learning New Addresses analysis (Section 7 in the paper) can be reproduced by running the following notebook:

* `learning-new-addrs-analysis.ipynb`


### Section 8: rDNS As A Data Source

The results from the rDNS As A Data Source analysis (Section 8 in the paper) can be reproduced by running the following notebook:

* `rdns-analysis.ipynb`


### Section 9: Client IPv6 Addresses

Due to privacy protection reasons we refrain from publishing raw data (i.e. client IPv6 addresses) and accompanying analysis.
You can find code and documentation on how to replicate our measurement study on the [paper website](https://ipv6hitlist.github.io/) and [this Github repository](https://github.com/qblone/crowdsourcing-ipv6).


### Tools

You can find tools used in the notebook analysis in the tools/ subfolder.
Python tools are published as source code, Go tools are published as source code and compiled code.
We publish the following tools:

* `iptopfxas.py`: Map IP addresses to prefix and AS using the pyasn module.
* `ipv6exploder.go`: Convert IPv6 addresses to their exploded/expanded version for consistency.
* `entropy-clustering`: Group IPv6 networks by entropy profiles. Source on [Github](https://github.com/pforemski/entropy-clustering/tree/IMC18).
* `zesplot`: Visualize IPv6 prefixes and addresses, x64 binary. Source on [Github](https://github.com/zesplot/zesplot/tree/IMC18).


## Data

The following data files can be found in the `data/` subfolder:

* `apd/`: Input and output files of APD processing, used in the aliased prefix detection analysis.
  * `2018-04-25-2300.csv.dpdprefix.pfxonly.sortu.icmp.dense`: List of aliased prefixes based on prefix-based measurements on 2018-04-25.
  * `2018-05-*-2300.csv.dpdtarget.slash*.threshold.pfxonly.randomips.pfxonly.sortu.sw3.dense`: List of aliased prefixes based on target-based measurements on different prefix levels applied with a 3-day sliding window in May 2018.
  * `2018-05-*-2300.csv.dpdtarget.slash*.threshold.pfxonly.randomips.pfxonly.sortu.sw3.nondense`: List of non-aliased prefixes based on target-based measurements on different prefix levels applied with a 3-day sliding window in May 2018.
  * `2018-05-*-2300.csv.dpdtarget.slash*.threshold.pfxonly.randomips.iponly.shuf.icmp`: ZMap CSV output files (first line contains header) of target-based ICMPv6 alias detection measurements on different prefix levels in May 2018.
  * `2018-05-*-2300.csv.dpdtarget.slash*.threshold.pfxonly.randomips.iponly.shuf.tcp80`: ZMap CSV output files (first line contains header) of target-based TCP-SYN port 80 alias detection measurements on different prefix levels in May 2018.
  * `2018-05-*-2300.csv.dpdtarget.slash*.threshold.pfxonly.randomips.iponly.shuf.joined.success.iponly.sortu.join.pfxonly.sort.uniqc`: Number of answers per prefix (maximum is 16) of target-based measurements on different prefix levels in May 2018.
  * `2018-05-11-2300.csv.dpdprefix.iponly.shuf`: List of target addresses for prefix-based measurements on 2018-05-11.
  * `2018-05-11-2300.csv.dpdprefix.pfxonly.sortu.sw3.dense`: List of aliased prefixes based on prefix-based measurements applied with a 3-day sliding window on 2018-05-11.
  * `2018-05-11-2300.csv.dpdtarget.slash*.threshold.pfxonly.randomips.iponly.shuf`: List of target addresses for target-based measurements on different prefix levels on 2018-05-11.
  * `slidingwindow_eval/`: Files to analyze APD sliding window effectiveness.
    * `2018-0*-*-2300.csv.dpdprefix.pfxonly.sortu.sw*.dense`: List of alised prefixes based on prefix-based measurements applied with different values for sliding window (0, 1, 2, 3, 5, 7 days) in April and May 2018.
* `input/`: Input files used in sources and other analyses.
  * `2018-05-*.txt.expl.sortu.shuf.wl.bl.dpd.nondense.iponly`: List of non-aliased input addresses for measurements in May 2018.
  * `2018-05-10.txt.expl.sortu`: List of raw input addresses for measurements on 2018-05-10.
  * `2018-05-10.txt.expl.sortu.shuf.wl.bl.dpd.nondense.iponly.pfxas`: List of non-aliased input addresses mapped to prefixes and ASes for measurements on 2018-05-10.
  * `2018-05-11.txt.expl.sortu.shuf.wl.bl`: List of input addresses for measurements on 2018-05-11.
  * `2018-05-11.txt.expl.sortu.shuf.wl.bl.murdock.nondense`: List of input addresses with Murdock et al.'s dealiasing technique applied for measurements on 2018-05-11.
  * `2018-05-11.txt.expl.sortu.shuf.wl.bl.slash96.sortu.ips`: List of input addresses and corresponding /96 prefixes for Murdock et al.'s dealiasing measurements on 2018-05-11.
  * `2018-05-11.txt.expl.sortu.shuf.wl.bl.slash96.sortu.ips.sortips.resp.pfxonly.sort.uniqc.three.pfxonly`: List of /96 prefixes detected as aliased by Murdock et al.'s dealiasing technique measurements on 2018-05-11.
  * `runup/`: Files to attribute IPv6 addresses to sources, used in the sources and probing analyses.
    * `2018-05-10.dltlbl`: Input addresses based on domain lists sources for measurements on 2018-05-10.
    * `2018-05-10.dltlbl.fdns`: Input addresses based on domain lists and DNS ANY sources for measurements on 2018-05-10.
    * `2018-05-10.dltlbl.fdns.ct`: Input addresses based on domain lists, DNS ANY, and Certificate Transparency sources for measurements on 2018-05-10.
    * `2018-05-10.dltlbl.fdns.ct.axfr`: Input addresses based on domain lists, DNS ANY, Certificate Transparency, and AXFR sources for measurements on 2018-05-10.
    * `2018-05-10.dltlbl.fdns.ct.axfr.bit`: Input addresses based on domain lists, DNS ANY, Certificate Transparency, AXFR, and Bitnodes sources for measurements on 2018-05-10.
    * `2018-05-10.dltlbl.fdns.ct.axfr.bit.ra`: Input addresses based on domain lists, DNS ANY, Certificate Transparency, AXFR, Bitnodes, and RIPE Atlas sources for measurements on 2018-05-10.
    * `2018-05-10.dltlbl.fdns.ct.axfr.bit.ra.scamper`: Input addresses based on domain lists, DNS ANY, Certificate Transparency, AXFR, Bitnodes, RIPE Atlas, and traceroute sources for measurements on 2018-05-10.
    * `2018-05-11.bitnodes.wl.bl.cum.join`: Input addresses based on Bitnodes source for measurements on 2018-05-11.
    * `2018-05-11.ct.cum.join`: Input addresses based on Certificate Transparency source for measurements on 2018-05-11.
    * `2018-05-11.dltlbl.fdns.ct.axfr.bit.ra.scamper.join`: Input addresses based on domain lists, DNS ANY, Certificate Transparency, AXFR, Bitnodes, and RIPE Atlas sources for measurements on 2018-05-11.
    * `2018-05-11.dltl.cum.join`: Input addresses based on domain lists source for measurements on 2018-05-11.
    * `axfr_2018-05-11.merged.cum.join`: Input addresses based on AXFR source for measurements on 2018-05-11.
    * `fdns-2018-05-11.wl.bl.cum.join`: Input addresses based on DNS ANY source for measurements on 2018-05-11.
    * `merged_cumsum/`: Files to reproduce cumulative sources runup of Figure 1a.
      * `201*-*-*.join.wcl`: Cumulative number of input addresses per source (output of `wc -l`) over time from April 2017 to May 2018.
* `learning-new-addrs/`: Files to reproduce 6Gen and Entropy/IP results.
  * `6gen/`: Result files from 6Gen address learning.
    * `joined.txt`: Joined list of addresses generated for each prefix by 6Gen.
    * `joined.txt.sortu`: Joined list of unique addresses generated for each prefix by 6Gen.
    * `joined.txt.sortu.wl`: Joined list of unique addresses whitelisted by routed prefixes generated for each prefix by 6Gen.
    * `joined.txt.sortu.wl.bl`: Joined list of unique addresses whitelisted by routed prefixes and excluding blacklisted addresses generated for each prefix by 6Gen.
    * `joined.txt.sortu.wl.bl.new`: Joined list of unique addresses whitelisted by routed prefixes, excluding blacklisted and previously known addresses generated for each prefix by 6Gen.
    * `joined.txt.sortu.wl.bl.new.noeip`: Joined list of unique addresses whitelisted by routed prefixes, excluding blacklisted and previously known addresses generated for each prefix by 6Gen which have not been generated by Entropy/IP.
  * `eip/`: Result files from Entropy/IP address learning.
    * `joined.txt`: Joined list of addresses generated for each prefix by Entropy/IP.
    * `joined.txt.sortu`: Joined list of unique addresses generated for each prefix by Entropy/IP.
    * `joined.txt.sortu.wl`: Joined list of unique addresses whitelisted by routed prefixes generated for each prefix by Entropy/IP.
    * `joined.txt.sortu.wl.bl`: Joined list of unique addresses whitelisted by routed prefixes and excluding blacklisted addresses generated for each prefix by Entropy/IP.
    * `joined.txt.sortu.wl.bl.new`: Joined list of unique addresses whitelisted by routed prefixes, excluding blacklisted and previously known addresses generated for each prefix by Entropy/IP.
  * `joined/`: Output files from measurements of 6Gen and Entropy/IP addresses.
    * `joined.txt.out.*`: ZMap CSV output files (first line contains header) for joined 6Gen and Entropy/IP address input list for different targeted protocols (ICMPv6, TCP/80, TCP/443, UDP/53, UDP/443).
* `misc/`: Miscellaneous files (e.g. RIB files) used in different analyses.
  * `2018-04-25-2300.icmp.addresses.dense`: List of dense addresses found in ICMPv6 measurements on 2018-04-25.
  * `clusters-full.txt`: List of (ASN, cluster) tuples for complete list of input addresses.
  * `clusters-hitlist.txt`: Output file of Entropy Clustering tool containing clusters based on the complete input addresses.
  * `clusters-hitlist-iid.txt`: Output file of Entropy Clustering tool containing clusters based on the interface identifier part of input addresses.
  * `clusters-udp53.txt`: Output file of Entropy Clustering tool containing clusters based on responsive UDP/53 addresses.
  * `profiles-hitlist.csv`: Output file of Entropy Profiles tool containing entropy profiles of complete input addresses.
  * `profiles-udp53.csv`: Output file of Entropy Profiles tool containing entropy profiles based on responsive UDP/53 addresses.
  * `rib.20180510.1200.bz2`: CAIDA's IPv6 Routeviews RIB file for AS and prefix mapping on 2018-05-10.
  * `rib.20180511.1200.bz2`: CAIDA's IPv6 Routeviews RIB file for AS and prefix mapping on 2018-05-11.
  * `rib.20180515.0600.bz2`: CAIDA's IPv6 Routeviews RIB file for AS and prefix mapping on 2018-05-15.
  * `routeviews_april25.txt`: CAIDA's IPv6 Routeviews file containing prefixes and ASes on 2018-04-25.
  * `routeviews_may11.txt`:  CAIDA's IPv6 Routeviews file containing prefixes and ASes on 2018-05-11.
* `output/`: ZMapv6 output files, used e.g. in probing analysis.
  * `2018-0*-*-2300.csv.*`: ZMap CSV output files (first line contains header) of IPv6 measurement results for different protocols (ICMPv6, TCP/80, TCP/443, UDP/53, UDP/443) in April and May 2018.
* `rdns/`: Input and output files of rDNS analysis.
  * `dataset.json.addr.sortu`: List of IPv6 addresses extracted from Tobias Fiebig's rDNS measurements.
  * `dataset.json.addr.sortu.wl`: List of IPv6 addresses extracted from Tobias Fiebig's rDNS measurements whitelisted by routed prefixes.
  * `dataset.json.addr.sortu.wl.bl`: List of IPv6 addresses extracted from Tobias Fiebig's rDNS measurements whitelisted by routed prefixes and excluding blacklisted addresses.
  * `dataset.json.addr.sortu.wl.bl.shuf.dpd.dense`: List of aliased IPv6 addresses extracted from Tobias Fiebig's rDNS measurements whitelisted by routed prefixes and excluding blacklisted addresses.
  * `dataset.json.addr.sortu.wl.bl.shuf.dpd.nondense`: List of non-aliased IPv6 addresses extracted from Tobias Fiebig's rDNS measurements whitelisted by routed prefixes and excluding blacklisted addresses.
  * `dataset.json.addr.sortu.wl.bl.shuf.dpd.nondense.iponly.out.*`:  ZMap CSV output files (first line contains header) of IPv6 measurement results of non-aliased IPv6 addresses extracted from Tobias Fiebig's rDNS measurements whitelisted by routed prefixes and excluding blacklisted addresses for different protocols (ICMPv6, TCP/80, TCP/443, UDP/53, UDP/443).

