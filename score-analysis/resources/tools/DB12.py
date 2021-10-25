from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import sys
import random
import multiprocessing
import json


if sys.version_info[0] < 3:
    # pylint: disable = E, W, R, C
    range = xrange


def single_dirac_benchmark(iterations_num=1, measured_copies=None):
    """Modified version of single_dirac_benchmark() that do not correct the norm"""
    # pylint: disable = too-many-locals
    # This number of iterations corresponds to 1kHS2k.seconds, i.e. 250 HS06 seconds
    iters = int(1000 * 1000 * 12.5)
    calib = 250.0
    if sys.version_info[0] < 3:
        # pylint: disable = E, W, R, C
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


def single_dirac_benchmark_process(
    result_object, iterations_num=1, measured_copies=None, process_id=0
):
    """Modified version of single_dirac_benchmark_process() that records the result of each benchmark run"""

    benchmark_result = single_dirac_benchmark(
        iterations_num=iterations_num, measured_copies=measured_copies
    )

    if not benchmark_result or "NORM" not in benchmark_result:
        return

    # This makes it easy to use with multiprocessing.Process
    benchmark_result["ITER"] = process_id
    with open("res_%d.json" % process_id, "w") as f:
        json.dump(benchmark_result, f)
    result_object.value = 0


def multiple_dirac_benchmark(copies=1, iterations_num=1, extra_iter=False):
    """Modified version of multiple_dirac_benchmark() that record the result of each benchmark run"""

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
        results.append(multiprocessing.Value("i", 0))
        processes.append(
            multiprocessing.Process(
                target=single_dirac_benchmark_process,
                args=(results[i], iterations_num, measured_copies, i),
            )
        )

    # Start them all off at the same time
    for process in processes:
        process.start()

    # Wait for them all to finish
    for process in processes:
        process.join()

    raw = []
    i = 0
    for res in results:
        with open("res_%d.json" % i, "r") as f:
            benchmark_result = json.load(f)
        raw.append(benchmark_result)
        i += 1

    raw.sort()

    # Return the list of raw results and various averages
    return raw


if __name__ == "__main__":

    output_path = "result_db12.json"
    if len(sys.argv) == 4:
        print(sys.argv)
        output_path = sys.argv[1]
        choice = sys.argv[2]
        numberProcesses = int(sys.argv[3])

    if choice == "single":
        score = single_dirac_benchmark()
        numberProcesses = 1
        score["ITER"] = 1
        scores = [score]
    elif choice == "multi":
        scores = multiple_dirac_benchmark(numberProcesses)
    else:
        sys.exit(1)

    i = 0
    for score in scores:
        score["COPIES"] = numberProcesses
        score["TYPE"] = choice

    output = {}
    output["scores"] = scores
    major, minor, micro = sys.version_info[:3]
    output["PythonVersion"] = {}
    output["PythonVersion"]["Major"] = major
    output["PythonVersion"]["Minor"] = minor
    output["PythonVersion"]["Micro"] = micro

    print(output)
    with open(output_path, "w") as f:
        json.dump(output, f)
