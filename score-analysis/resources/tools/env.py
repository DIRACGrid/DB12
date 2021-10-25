from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import sys
import socket
import json


def get_environment_details():
    env = {}
    env["Uname"] = " ".join(os.uname())
    env["HostName"] = socket.gethostname()
    env["HostFQDN"] = socket.getfqdn()

    fileName = "/etc/redhat-release"
    if os.path.exists(fileName):
        with open(fileName, "r") as f:
            env["RedHatRelease"] = f.read().strip()

    fileName = "/etc/lsb-release"
    if os.path.isfile(fileName):
        with open(fileName, "r") as f:
            env["Linux release"] = f.read().strip()

    fileName = "/proc/cpuinfo"
    if os.path.exists(fileName):
        with open(fileName, "r") as f:
            cpu = f.readlines()
        nCPU = 0
        for line in cpu:
            if line.find("cpu MHz") == 0:
                nCPU += 1
                freq = line.split()[3]
            elif line.find("model name") == 0:
                CPUmodel = line.split(": ")[1].strip()
        env["CPUModel"] = CPUmodel
        env["CPUMHz"] = "%s x %s" % (nCPU, freq)

    fileName = "/proc/meminfo"
    if os.path.exists(fileName):
        with open(fileName, "r") as f:
            mem = f.readlines()
        freeMem = 0
        for line in mem:
            if line.find("MemTotal:") == 0:
                totalMem = int(line.split()[1])
            if line.find("MemFree:") == 0:
                freeMem += int(line.split()[1])
            if line.find("Cached:") == 0:
                freeMem += int(line.split()[1])
        env["MemorykB"] = totalMem
        env["FreeMem.kB"] = freeMem

    return env


if __name__ == "__main__":

    output_path = "env.json"
    if len(sys.argv) == 2:
        output_path = sys.argv[1]

    env = get_environment_details()
    with open(output_path, "w") as f:
        json.dump(env, f)
