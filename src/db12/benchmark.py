"""Contains all the functions needed to run DB12"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import sys
import random
import multiprocessing

if sys.version_info[0] < 3:
    #pylint: disable = E, W, R, C
    range = xrange

def single_dirac_benchmark(iterations_num=1, measured_copies=None):
    """Get Normalized Power of one CPU in DIRAC Benchmark 2012 units (DB12)"""
    #pylint: disable = too-many-locals
    # This number of iterations corresponds to 1kHS2k.seconds, i.e. 250 HS06 seconds

    iters = int(1000 * 1000 * 12.5)
    calib = 250.0
    if sys.version_info[0] < 3:
        #pylint: disable = E, W, R, C
        m_1 = long(0)
        m_2 = long(0)
    else:
        m_1 = int(0)
        m_2 = int(0)
    p_1 = 0
    p_2 = 0
    # Do one iteration extra to allow CPUs with variable speed (we ignore zeroth iteration)
    # Do one or more extra iterations to avoid tail effects when copies run in parallel
    it_1 = 0
    while (it_1 <= iterations_num) or (
            measured_copies is not None and measured_copies.value > 0
    ):
        if it_1 == 1:
            start = os.times()

        # Now the iterations
        for _j in range(iters):
            t_1 = random.normalvariate(10, 1)
            m_1 += t_1
            m_2 += t_1 * t_1
            p_1 += t_1
            p_2 += t_1 * t_1

        if it_1 == iterations_num:
            end = os.times()
            if measured_copies is not None:
                # Reduce the total of running copies by one
                measured_copies.value -= 1

        it_1 += 1

    cput = sum(end[:4]) - sum(start[:4])
    wall = end[4] - start[4]

    if not cput:
        return None

    # Return DIRAC-compatible values
    output = {
        "CPU": cput,
        "WALL": wall,
        "NORM": calib * iterations_num / cput,
        "UNIT": "DB12",
    }
    return output

def single_dirac_benchmark_process(result_object, iterations_num=1, measured_copies=None):
    """Run single_dirac_benchmark() in a multiprocessing friendly way"""

    benchmark_result = single_dirac_benchmark(
        iterations_num=iterations_num, measured_copies=measured_copies
    )

    if not benchmark_result or "NORM" not in benchmark_result:
        return

    # This makes it easy to use with multiprocessing.Process
    result_object.value = benchmark_result["NORM"]

def multiple_dirac_benchmark(copies=1, iterations_num=1, extra_iter=False):
    """Run multiple copies of the DIRAC Benchmark in parallel"""

    processes = []
    results = []

    if extra_iter:
        # If true, then we run one or more extra iterations in each
        # copy until the number still being meausured is zero.
        measured_copies = multiprocessing.Value("i", copies)
    else:
        measured_copies = None

    # Set up all the subprocesses
    for i in range(copies):
        results.append(multiprocessing.Value("d", 0.0))
        processes.append(
            multiprocessing.Process(
                target=single_dirac_benchmark_process,
                args=(results[i], iterations_num, measured_copies),
            )
        )

    # Start them all off at the same time
    for process in processes:
        process.start()

    # Wait for them all to finish
    for process in processes:
        process.join()

    raw = []
    product = 1.0

    for res in results:
        raw.append(res.value)
        product *= res.value

    raw.sort()

    # Return the list of raw results and various averages
    output = {
        "raw": raw,
        "copies": copies,
        "sum": sum(raw),
        "arithmetic_mean": sum(raw) / copies,
        "geometric_mean": product ** (1.0 / copies),
        "median": raw[(copies - 1) // 2],
    }
    return output

def wholenode_dirac_benchmark(copies=None, iterations_num=1, extra_iter=False):
    """Run as many copies as needed to occupy the whole machine"""

    # If not given by caller then just count CPUs
    if copies is None:
        try:
            copies = multiprocessing.cpu_count()
        except: # pylint: disable=bare-except
            copies = 1

    return multiple_dirac_benchmark(
        copies=copies, iterations_num=iterations_num, extra_iter=extra_iter
    )


def jobslot_dirac_benchmark(copies=None, iterations_num=1, extra_iter=False):
    """Run as many copies as needed to occupy the job slot"""

    # If not given by caller then just run one copy
    if copies is None:
        copies = 1

    return multiple_dirac_benchmark(
        copies=copies, iterations_num=iterations_num, extra_iter=extra_iter
    )
