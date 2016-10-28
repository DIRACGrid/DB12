#!/usr/bin/python

########################################################################
# File :    DIRACbenchmark.py
# Author :  Andrew McNab 
########################################################################

""" DIRAC Benchmark 2012 by Ricardo Graciani, and wrapper functions to
    run multiple instances in parallel by Andrew McNab.
    
    This file (DIRACbenchmark.py) is intended to be the ultimate upstream
    shared by different users of the DIRAC Benchmark 2012 (DB12). The
    canonical version can be found at https://github.com/DIRACGrid/DB12
"""

import os
import sys
import random
import urllib
import multiprocessing

version = '0.1 DB12'

def singleDiracBenchmark( iterations = 1 ):
  """ Get Normalized Power of one CPU in DIRAC Benchmark 2012 units (DB12)
  """

  # This number of iterations corresponds to 1kHS2k.seconds, i.e. 250 HS06 seconds

  n = int( 1000 * 1000 * 12.5 )
  calib = 250.0

  m = long( 0 )
  m2 = long( 0 )
  p = 0
  p2 = 0
  # Do one iteration extra to allow CPUs with variable speed (we ignore zeroth iteration)
  for i in range( iterations + 1 ):
    if i == 1:
      start = os.times()
    # Now the iterations
    for _j in xrange( n ):
      t = random.normalvariate( 10, 1 )
      m += t
      m2 += t * t
      p += t
      p2 += t * t

  end = os.times()
  cput = sum( end[:4] ) - sum( start[:4] )
  wall = end[4] - start[4]

  if not cput:
    return None
  
  # Return DIRAC-compatible values
  return { 'CPU' : cput, 'WALL' : wall, 'NORM' : calib * iterations / cput, 'UNIT' : 'DB12' }

def singleDiracBenchmarkProcess( resultObject, iterations = 1 ):

  """ Run singleDiracBenchmark() in a multiprocessing friendly way
  """

  benchmarkResult = singleDiracBenchmark( iterations )
  
  if not benchmarkResult or 'NORM' not in benchmarkResult:
    return None
    
  # This makes it easy to use with multiprocessing.Process
  resultObject.value = benchmarkResult['NORM']

def multipleDiracBenchmark( instances = 1, iterations = 1 ):

  """ Run multiple instances of the DIRAC Benchmark in parallel  
  """

  processes = []
  results = []

  # Set up all the subprocesses
  for i in range( instances ):
    results.append( multiprocessing.Value('d', 0.0) )
    processes.append( multiprocessing.Process( target = singleDiracBenchmarkProcess, args = ( results[i], iterations ) ) )
 
  # Start them all off at the same time 
  for p in processes:  
    p.start()
    
  # Wait for them all to finish
  for p in processes:
    p.join()

  raw = [ result.value for result in results ]

  # Return the list of raw results, and the sum and mean of the list
  return { 'raw' : raw, 'sum' : sum(raw), 'mean' : sum(raw)/len(raw) }
  
def wholenodeDiracBenchmark( instances = None, iterations = 1 ): 

  """ Run as many instances as needed to occupy the whole machine
  """
  
  # Try $MACHINEFEATURES first if not given by caller
  if not instances and 'MACHINEFEATURES' in os.environ:
    try:
      instances = int( urllib2.urlopen( os.environ['MACHINEFEATURES'] + '/total_cpu' ).read() )
    except:
      pass

  # If not given by caller or $MACHINEFEATURES/total_cpu then just count CPUs
  if not instances:
    try:
      instances = multiprocessing.cpu_count()
    except:
      instances = 1
  
  return multipleDiracBenchmark( instances = instances, iterations = iterations )
  
def jobslotDiracBenchmark( instances = None, iterations = 1 ):

  """ Run as many instances as needed to occupy the job slot
  """

  # Try $JOBFEATURES first if not given by caller
  if not instances and 'JOBFEATURES' in os.environ:
    try:
      instances = int( urllib2.urlopen( os.environ['JOBFEATURES'] + '/allocated_cpu' ).read() )
    except:
      pass

  # If not given by caller or $JOBFEATURES/allocated_cpu then just run one instance
  if not instances:
    instances = 1
  
  return multipleDiracBenchmark( instances = instances, iterations = iterations )

#
# If we run as a command
#   
if __name__ == "__main__":

  if len(sys.argv) == 1 or sys.argv[1] == 'single':
    print singleDiracBenchmark()['NORM']
    sys.exit(0)

  if sys.argv[1] == 'version':
    print version
    sys.exit(0)

  if sys.argv[1] == 'wholenode':
    result = wholenodeDiracBenchmark()
    print result['mean'],result['sum'],result['raw']
    sys.exit(0)

  if sys.argv[1] == 'jobslot':
    result = jobslotDiracBenchmark()
    print result['mean'],result['sum'],result['raw']
    sys.exit(0)

  try:
    instances = int( sys.argv[1] )
  except:
    sys.exit(1)
  else:
    result = multipleDiracBenchmark(instances = instances)
    print result['mean'],result['sum'],result['raw']
    sys.exit(0)
