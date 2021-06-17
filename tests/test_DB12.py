"""Unit test for DB12"""
from __future__ import absolute_import
from __future__ import division
import pytest

from db12 import single_dirac_benchmark
from db12 import multiple_dirac_benchmark
from db12 import wholenode_dirac_benchmark
from db12 import jobslot_dirac_benchmark

@pytest.mark.parametrize(
    "copies, iterations, extra_iteration",
    [
        ("single", 1, False),
        ("single", 2, True),
        ("wholenode", 1, False),
        ("wholenode", 2, True),
        ("jobslot", 1, False),
        ("jobslot", 2, True),
        (2, 1, False),
        (3, 2, True),
    ],
)

def test_dirac_benchmark(copies, iterations, extra_iteration):
    """ Testing each function in the DB12 to make sure that:
    1- It produces the same output when run with the same input
    2- It produces the same output when run with a different number of iterations
    """
    k = 0
    threshold = 20/100

    if copies is None or copies == "single":
        result = single_dirac_benchmark(iterations_num=iterations)["NORM"]
        result2 = single_dirac_benchmark(iterations_num=iterations)["NORM"]
        result3 = single_dirac_benchmark(iterations_num=iterations + 1)["NORM"]

        assert abs(result2 - result) <= result * threshold
        assert abs(result3 - result) <= result * threshold

        assert result >= 0
        assert result < 100

    elif copies == "wholenode":
        result = wholenode_dirac_benchmark(
            iterations_num=iterations, extra_iter=extra_iteration
        )
        result2 = wholenode_dirac_benchmark(
            iterations_num=iterations, extra_iter=extra_iteration
        )
        result3 = wholenode_dirac_benchmark(
            iterations_num=iterations + 1, extra_iter=extra_iteration
        )

        assert result["geometric_mean"] >= 0 and result["geometric_mean"] < 100
        assert result["arithmetic_mean"] >= 0 and result["arithmetic_mean"] < 100
        assert result["median"] >= 0 and result["median"] < 100

        for i in result["raw"]:
            assert abs(i - result2["raw"][k]) <= result2["raw"][k] * threshold
            assert i >= 0
            assert i < 100
            k = k + 1

        k = 0
        for i in result2["raw"]:
            assert abs(i - result3["raw"][k]) <= result3["raw"][k] * threshold
            assert i >= 0
            assert i < 100
            k = k + 1

    elif copies == "jobslot":
        result = jobslot_dirac_benchmark(
            iterations_num=iterations, extra_iter=extra_iteration
        )
        result2 = jobslot_dirac_benchmark(
            iterations_num=iterations, extra_iter=extra_iteration
        )
        result3 = jobslot_dirac_benchmark(
            iterations_num=iterations + 1, extra_iter=extra_iteration
        )

        assert result["geometric_mean"] >= 0 and result["geometric_mean"] < 100
        assert result["arithmetic_mean"] >= 0 and result["arithmetic_mean"] < 100
        assert result["median"] >= 0 and result["median"] < 100

        for i in result["raw"]:
            assert abs(i - result2["raw"][k]) <= result2["raw"][k] * threshold
            assert i >= 0
            assert i < 100
            k = k + 1

        k = 0
        for i in result2["raw"]:
            assert abs(i - result3["raw"][k]) <= result3["raw"][k] * threshold
            assert i >= 0
            assert i < 100
            k = k + 1
    else:
        result = multiple_dirac_benchmark(
            copies=int(copies), iterations_num=iterations, extra_iter=extra_iteration
        )
        result2 = multiple_dirac_benchmark(
            copies=int(copies), iterations_num=iterations, extra_iter=extra_iteration
        )
        result3 = multiple_dirac_benchmark(
            copies=int(copies), iterations_num=iterations + 1, extra_iter=extra_iteration
        )

        assert result["geometric_mean"] >= 0 and result["geometric_mean"] < 100
        assert result["arithmetic_mean"] >= 0 and result["arithmetic_mean"] < 100
        assert result["median"] >= 0 and result["median"] < 100

        for i in result["raw"]:
            assert abs(i - result2["raw"][k]) <= result2["raw"][k] * threshold
            assert i >= 0
            assert i < 100
            k = k + 1

        k = 0
        for i in result2["raw"]:
            assert abs(i - result3["raw"][k]) <= result3["raw"][k] * threshold
            assert i >= 0
            assert i < 100
            k = k + 1
