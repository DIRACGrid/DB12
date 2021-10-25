# Analysis of the scores

DB12 has been originally conceived with Python2 to estimate the power of a given CPU to run HEP applications.
However, since January 2020, Python2 is no [longer maintained](https://www.python.org/doc/sunset-python-2/) and we decided to port the code to Python3, which contains several optimizations.

In October 2021, we effectively ported DB12 to Python3.9, but the optimizations brought by the language generated discrepancies in the norm score,
which is a critical component to evaluate the power of CPUs.
We build an analysis tool to mitigate these discrepancies.

## Current situation

The current analysis assess the impact of the changes on the norm score and propose 3 different solutions to resolve the issue:
- Find a constant value that would transform a python3 score into a python2 one: 1.18 seems fine.
  - Pros: simple
  - Cons: not accurate. does fit well with scores computed on Intel, not so well with scores computed on AMD
- Find one constant value per processor type (Intel/AMD): 1.16 fits well with scores computed on Intel, 1.4 also fits well with scores computed on AMD .
  - Pros: accurate
  - Cons: need to maintain a table and update it with new types of processors, and maybe also with new versions of python
- Compute a simple linear regression:
  - Pros: accurate
  - Cons: need to run it with many examples to get an accurate model

To keep it simple and accurate, we chose to apply the second solution: one constant value per processor type.
These constants are part of the code and are located in `src/db12/factors.json`.

These values will need to be updated through time, according to the evolution of the CPUs and Python.
If you need to get an accurate DB12 norm score using a Python version or a CPU that has not be taken into account,
then you have to run the analysis with new data following the next steps.

## Run the analysis

Execute the Jupyter Notebook:

```bash
jupyter notebook score-analysis/DB12Analysis.ipynb
```

## Include new data using DIRAC

- Install a DIRAC client:

```bash
lb-dirac
lhcb-proxy-init
```

- Go to `score-analysis/resources/tools` and submit jobs:

```bash
./submit.sh <number of jobs> <list of sites>
```

- Once the jobs are done, add their IDs in `jobIDs.csv` to get the results:

```bash
python getDB12Scores.py
```

- You will obtain `results.json`, you can sort the file to get a better look at it with `jq`:

```bash
cat results.json | jq . > results_sorted_<date>.json
```

- You can finally remove the jobs that are still pending in the queues
