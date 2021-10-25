import argparse
import os
import shutil
import sys

# from DIRAC.Core.Base import Script
# Script.parseCommandLine( ignoreErrors = True )

from DIRAC.Interfaces.API.Job import Job
from DIRAC.Interfaces.API.Dirac import Dirac


def parseArgs():
    parser = argparse.ArgumentParser(description="Parser of DB12 Submitter")
    parser.add_argument("--target", type=str)
    parser.add_argument("--njobs", type=int, default=1)
    parser.set_defaults(func=submitJob)

    args = parser.parse_args()
    args.func(args)
    # Explicitly exit to make testing easier
    sys.exit(0)


def submitJob(args):
    dirac = Dirac()

    if args.target:
        with open(args.target, "r") as f:
            sitesStr = f.read()
            sites = sitesStr.split("\n")
    else:
        sites = ["ANY"]

    for site in sites:
        if not site:
            continue
        for i in range(args.njobs):
            job = generateJob(site, "executable.sh")
            jdl = job._toJDL()
            result = dirac.submitJob(job)
            print(result)


def generateJob(target, executable):
    j = Job()
    j.setName("DB12")
    j.setJobGroup("lhcb")
    j.setInputSandbox(["DB12.py", "env.py"])
    j.setOutputSandbox(["outputs", "env.json"])
    j.setCPUTime(35000)
    j.setLogLevel("DEBUG")
    if target != ["ANY"]:
        j.setDestination(target)
    j.setExecutable("./%s" % executable)
    return j


if __name__ == "__main__":
    parseArgs()
