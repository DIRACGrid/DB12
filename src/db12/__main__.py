""" DIRAC Benchmark 2012 by Ricardo Graciani, and wrapper functions to
    run multiple copies in parallel by Andrew McNab.
    This file (dirac_benchmark.py) is intended to be the ultimate upstream
    shared by different users of the DIRAC Benchmark 2012 (DB12). The
    canonical version can be found at https://github.com/DIRACGrid/DB12
    This script can either be imported or run from the command line:
    ./dirac_benchmark.py NUMBER
    where NUMBER gives the number of benchmark processes to run in parallel.
    Run  ./dirac_benchmark.py help  to see more options.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import argparse
import json
from pkg_resources import get_distribution, DistributionNotFound

from db12 import single_dirac_benchmark
from db12 import multiple_dirac_benchmark
from db12 import wholenode_dirac_benchmark

try:
    VERSION = get_distribution("db12").version
except DistributionNotFound:
    pass


def dump_as_json(filename, output):
    """Function to save result to a json file

    :param str filename: path to a json file
    :param dict output: content to dump in the json file
    """
    with open(filename, "w") as outfile:
        json.dump(output, outfile)


def single_dirac_benchmark_cli(args):
    """Function that calls single_dirac_benchmark and prints
    its results/calls dump_as_json"""
    result = single_dirac_benchmark(
        iterations_num=args.iterations, correction=args.correction
    )["NORM"]
    if args.json:
        dump_as_json(args.json, result)
    else:
        print(result)


def multiple_dirac_benchmark_cli(args):
    """Function that calls multiple_dirac_benchmark and prints
    its results/calls dump_as_json"""
    result = multiple_dirac_benchmark(
        copies=args.copies,
        iterations_num=args.iterations,
        extra_iter=args.extra_iteration,
        correction=args.correction,
    )
    if args.json:
        dump_as_json(args.json, result)
    else:
        print(
            result["copies"],
            result["sum"],
            result["arithmetic_mean"],
            result["geometric_mean"],
            result["median"],
        )
        print(" ".join([str(k) for k in result["raw"]]))


def wholenode_dirac_benchmark_cli(args):
    """Function that calls wholenode_dirac_benchmark and prints
    its results/calls dump_as_json"""
    result = wholenode_dirac_benchmark(
        iterations_num=args.iterations,
        extra_iter=args.extra_iteration,
        correction=args.correction,
    )
    if args.json:
        dump_as_json(args.json, result)
    else:
        print(
            result["copies"],
            result["sum"],
            result["arithmetic_mean"],
            result["geometric_mean"],
            result["median"],
        )
        print(" ".join([str(j) for j in result["raw"]]))


def main():
    """Uses the functions within dirac_benchmark.py to run the DB12 benchmark from
    the command line: single, jobslots, multiple and wholenode.
    By default, one benchmarking iteration is run, in addition to the initial
    iteration which DB12 runs and ignores to avoid ramp-up effects at the start.
    The number of benchmarking iterations can be increased using the --iterations
    option. Additional iterations which are also ignored can be added with the
    --extra-iteration option to avoid tail effects. In this case copies which
    finish early run additional iterations until all the measurements finish.
    The copies (ie an integer) argument causes multiple copies of the benchmark to
    be run in parallel. Unless the token "single" is used, the script prints the
    following results to two lines on stdout:
    COPIES SUM ARITHMETIC-MEAN GEOMETRIC-MEAN MEDIAN
    RAW-RESULTS"""

    help_string = """Run the DB12 benchmark from the command line.
Unless the token "single" is used, the script prints the following results to
two lines on stdout:
COPIES SUM ARITHMETIC-MEAN GEOMETRIC-MEAN MEDIAN
RAW-RESULTS
"""

    # Common arguments: --iterations, --json, --no-correction
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--iterations",
        nargs="?",
        type=int,
        help="number of iterations to perform",
        default=1,
    )
    parent_parser.add_argument("--json", help="generate json files", type=str)
    parent_parser.add_argument(
        "--no-correction",
        help="Disable norm correction",
        dest="correction",
        action="store_false",
    )

    # Main parser
    parser = argparse.ArgumentParser(description=help_string)
    parser.add_argument("--version", action="version", version=VERSION, default="")

    # Subparser: single benchmark
    subparsers = parser.add_subparsers()
    parser_single = subparsers.add_parser(
        "single", help="get normalized power of one CPU", parents=[parent_parser]
    )
    parser_single.set_defaults(func=single_dirac_benchmark_cli)

    # Subparser: wholenode benchmark
    parser_wholenode = subparsers.add_parser(
        "wholenode",
        help="Run as many copies as needed to occupy the whole machine",
        parents=[parent_parser],
    )
    parser_wholenode.add_argument(
        "--extra-iteration",
        help="whether an extra iteration is needed",
        action="store_true",
    )
    parser_wholenode.set_defaults(func=wholenode_dirac_benchmark_cli)

    # Subparser: multiple benchmark
    parser_multiple = subparsers.add_parser(
        "multiple", help="Run multiple copies in parallel", parents=[parent_parser]
    )
    parser_multiple.add_argument("copies", type=int, help="number of copies")
    parser_multiple.add_argument(
        "--extra-iteration",
        help="whether an extra iteration is needed",
        action="store_true",
    )
    parser_multiple.set_defaults(func=multiple_dirac_benchmark_cli)

    # Get params and execute the selected function
    args = parser.parse_args()

    if hasattr(args, "func") and args.func:
        args.func(args)
    else:
        parser.print_help()


#
# If we run as a command
#
if __name__ == "__main__":
    main()
