import json
import glob
import re
import DIRAC
import os
import shutil
import tarfile
import re

from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Interfaces.API.DiracAdmin import DiracAdmin


def get_jobids(filename):
    with open(filename, "r") as f:
        jobids = f.read()
    jobids = jobids.split(",")
    return jobids


def get_db12scores(dirac, jobid):
    result = dirac.getOutputSandbox(jobid)
    if not result["OK"]:
        print("Oops didn't get output sandbox: %s" % result["Message"])
        shutil.rmtree(jobid)
        return None

    if not os.path.exists(jobid):
        print("Job output sandbox does not exist")
        return None

    print("Job output sandbox retrieved in %s/" % (jobid))
    scores = {}

    target_folder = "."
    with tarfile.open("%s/outputs.tar" % jobid) as tar:
        tar.extractall(jobid)

    for result_db12 in glob.glob("%s/outputs/result*.json" % jobid):
        iter, pyversion = re.findall("result(\d+).*(py\d).json", result_db12)[0]
        key = "%s_%s" % (iter, pyversion)
        with open(result_db12, "r") as f:
            content = json.load(f)
            scores[key] = content

    with open("%s/env.json" % jobid, "r") as f:
        scores["env"] = json.load(f)

    shutil.rmtree(jobid)
    return scores


def get_jobparams(dirac, jobid):
    result = dirac.getJobParameters(jobid)
    if not result["OK"]:
        print("Oops didn't get job parameters: %s" % result["Message"])
    return result["Value"]


def get_pilotattributes(dirac, jobid):
    result = dirac.getJobPilots(jobid)
    if not result["OK"]:
        print("Oops didn't get pilot attributes: %s" % result["Message"])
        return None

    pilotattributes = result["Value"]
    return pilotattributes


def get_pilotoutput(dirac, pilotid):
    result = dirac.getPilotOutput(pilotid)
    if not result["OK"]:
        print("Oops didn't get pilot output: %s" % result["Message"])
        return None

    pilotoutput = result["Value"].get("StdOut")
    if not pilotoutput:
        print("Oops pilot output is not available")
        return None

    cpu_mhz = re.findall("CPU \(MHz\).*= (.*)", pilotoutput)[0]
    cpu_model = re.findall("CPU \(model\).*= (.*)", pilotoutput)[0]
    os = re.findall("elease.*= (.*)", pilotoutput)[0]

    directory = "pilot_%s" % pilotid.split("/")[-1]
    shutil.rmtree(directory)
    return (cpu_mhz, cpu_model, os)


def main():
    jobids = get_jobids("jobIDs.csv")
    dirac = Dirac()
    dirac_admin = DiracAdmin()

    general_results = {}
    for jobid in jobids:
        jobid = jobid.strip()

        jobparams = {}
        pilotattr = {}
        os = None
        cpu_model = None
        cpu_mhz = None

        # First: get results from job output
        results = get_db12scores(dirac, jobid)
        if not results:
            print("Results are not available for %s" % jobid)
            continue

        # Second: get job parameters
        jobparams = get_jobparams(dirac, jobid)

        general_results[jobid] = {}
        general_results[jobid]["environment"] = results.pop("env")
        general_results[jobid]["jobparams"] = jobparams
        general_results[jobid]["results"] = {}
        for iteration, score in results.items():
            general_results[jobid]["results"][iteration] = score

    with open("results.json", "w") as f:
        json.dump(general_results, f)


if __name__ == "__main__":
    main()
