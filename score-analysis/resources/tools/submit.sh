#!/bin/bash
# 1: Number of jobs to submit per Site
# 2: List of sites in a csv format such as:
#    Site1
#    Site2
#    ...
set -x
dirac-proxy-init

NBJOBS=${1:-5}
SITES=${2:-"sites.csv"}


python submitDB12.py --njobs $NBJOBS --target $SITES
