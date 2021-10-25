"""Contains all the functions needed to run DB12"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import logging
import json
import sys
import random
import re
import multiprocessing

if sys.version_info[0] < 3:
    # pylint: disable = E, W, R, C
    # python3 range corresponds to xrange in python2
    range = xrange


def single_dirac_benchmark(iterations_num=1, measured_copies=None, correction=True):
    """Get Normalized Power of one CPU in DIRAC Benchmark 2012 units (DB12)

    :param int iterations_num: number of iterations to run
    :param multiprocessing.Value measured_copies: extra iterations to run
    """
    # pylint: disable = too-many-locals
    # This number of iterations corresponds to 1kHS2k.seconds, i.e. 250 HS06 seconds

    iters = int(1000 * 1000 * 12.5)
    calib = 250.0
    m_1 = int(0)
    m_2 = int(0)
    if sys.version_info[0] < 3:
        # pylint: disable = E, W, R, C
        # long type does not exist anymore in python3 but was used in this context with python2
        m_1 = long(0)
        m_2 = long(0)

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

    norm = calib * iterations_num / cput
    if correction:
        norm = get_norm_correction(norm)

    # Return DIRAC-compatible values
    output = {
        "CPU": cput,
        "WALL": wall,
        "NORM": norm,
        "UNIT": "DB12",
    }
    return output


def single_dirac_benchmark_process(
    result_object, iterations_num=1, measured_copies=None, correction=True
):
    """Run single_dirac_benchmark() in a multiprocessing friendly way

    :param multiprocessing.Value result_object: result to be returned
    :param int iterations_num: number of iterations to run
    :param multiprocessing.Value measured_copies: extra iterations to run
    """

    benchmark_result = single_dirac_benchmark(
        iterations_num=iterations_num,
        measured_copies=measured_copies,
        correction=correction,
    )

    if not benchmark_result or "NORM" not in benchmark_result:
        return

    # This makes it easy to use with multiprocessing.Process
    result_object.value = benchmark_result["NORM"]


def multiple_dirac_benchmark(
    copies=1, iterations_num=1, extra_iter=False, correction=True
):
    """Run multiple copies of the DIRAC Benchmark in parallel

    :param int copies: number of single benchmark to run in parallel
    :param int interations_num: number of iterations to run
    :param bool extra_iter: to know whether it should include extra iterations
    """

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
                args=(results[i], iterations_num, measured_copies, correction),
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


def wholenode_dirac_benchmark(iterations_num=1, extra_iter=False, correction=True):
    """Run as many copies as needed to occupy the whole machine

    :param int interations_num: number of iterations to run
    :param bool extra_iter: to know whether it should include extra iterations
    """

    try:
        copies = multiprocessing.cpu_count()
    except:  # pylint: disable=bare-except
        copies = 1

    return multiple_dirac_benchmark(
        copies=copies,
        iterations_num=iterations_num,
        extra_iter=extra_iter,
        correction=correction,
    )


def get_norm_correction(norm_computed):
    """Apply a factor on the norm depending on the python version used and
    the architecture targeted in order to reproduce the original norm from python2.

    :param float norm_computed: raw norm
    """
    # If python2 is used, then no action is needed
    if sys.version_info[0] < 3:
        return norm_computed

    logging.warn(
        "You are executing DB12 using python3, DB12 score is generally higher than it was with python2"
    )
    logging.warn("Trying to apply a correction...")

    # Get the dictionary of factors
    with open(
        os.path.join(os.path.dirname(__file__), "factors.json"), "r"
    ) as file_object:
        factor_dict = json.load(file_object)

    # Get Python version: if not in the dictionary, no action can be performed
    major, minor, micro = sys.version_info[0:3]
    python_version = "%s.%s.%s" % (major, minor, micro)
    if python_version not in factor_dict.keys():
        logging.warn(
            "Cannot correct the score, return the raw norm: the python version you are using has not been analyzed."
        )
        logging.warn(
            "Please consult https://zenodo.org/record/5647834 for further details"
        )
        return norm_computed

    # Get CPU brand name
    try:
        with open("/proc/cpuinfo", "r") as file_object:
            content = file_object.read()
        cpu_model_name = re.findall("model name\t: ([a-zA-Z]*) ", content)[0]
    except IOError:
        logging.warn(
            "Cannot correct the score, return the raw norm: cannot access CPU information"
        )
        return norm_computed

    factor = factor_dict[python_version].get(cpu_model_name)
    if not factor:
        logging.warn(
            "Cannot correct the score, return the raw norm: the CPU model you are using has not been analyzed."
        )
        logging.warn(
            "Please consult https://zenodo.org/record/5647834 for further details."
        )
        return norm_computed

    logging.info("Applying a factor of %s to the raw norm %s", factor, norm_computed)
    return norm_computed * factor
