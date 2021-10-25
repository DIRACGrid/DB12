#!/bin/bash
set -x
mkdir outputs

# Start 20 executions of db12 (10 python2, 10 python3)
for iteration in {0..10}; do

  # Get environment details
  /cvmfs/lhcb.cern.ch/lhcbdirac/v10r2p10/diracos/usr/bin/python env.py env.json

  # Run db12
  start=`date +%s`
  /cvmfs/lhcb.cern.ch/lhcbdirac/v10r2p10/diracos/usr/bin/python DB12.py outputs/result${iteration}_db12_py2.json single 1
  /cvmfs/lhcb.cern.ch/lhcbdirac/v10.2.10-x86_64/bin/python3 DB12.py outputs/result${iteration}_db12_py3.json single 1
  end=`date +%s`

  # Wait some time before continuing
  runtime=$(((end-start)/60))
  timeleft=$((5-runtime))
  sleep ${timeleft}m

done
