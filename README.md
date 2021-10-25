# DB12

DIRAC benchmark 2012 is a really quick benchmark, originally developed by Ricardo Graciani (https://github.com/graciani)
that uses wrapper functions by Andrew McNab (https://github.com/Andrew-McNab-UK) to run multiple copies in parallel.
Imane Iraoui (https://github.com/ImanIra0ui/) ported it to py3 and added many tests.
The current maintainers are Federico Stagni (https://github.com/fstagni) and Alexandre Boyer (https://github.com/aldbr).

It is distributed from https://github.com/DIRACGrid/DB12.

# Install

To install the DB12 package, run:

```bash
pip install DB12
```

# Use
## From the Command line interface

You can execute a single DB12 benchmark with the following command:

```bash
db12 single
```

To get further information, read the help:

```bash
db12 --help
```

## From your code

After installation, the package can be imported by typing:

```python
from db12 import single_dirac_benchmark
single_dirac_benchmark()
```

# Contribute
## Development

DB12 is a fully open source project, and you are welcome to contribute to it:
- Fork the project
- Develop
- Create a Pull Request to propose a change

## Code quality

To ensure the code meets DB12's coding conventions we recommend installing pre-commit system wide using your operating system's package manager.
Alteratively, pre-commit is included in the Python3 development environment, see the development guide for details on how to create one.
Once pre-commit is installed you can enable it by running:

```bash
pre-commit install --allow-missing-config
```

Code formatting will now be automatically applied before each commit.

## Score analysis

DB12 has been ported to Python3 in October 2021, this created discrepancies in the scores.
You might need to run an analysis of the DB12 scores to mitigate these discrepancies.

Further details: [here](https://zenodo.org/record/5647834)
