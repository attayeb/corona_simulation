The impact of community containment implementation timing on the spread of COVID-19: A simulation study
===================================================
Attayeb Mohsen and Ahmed Alarabi
---

This repository is the companion for the paper submitted to F1000Research ((https://doi.org/10.12688/f1000research.24156.1) [under peer review])

Repository files
================
* simulation.py: The main simulation code
* cli.py: Command line interface
* Summary-analysis.ipynb: Jupyter notebook for the analysis and figures creation
* Results/: folder contains the smmary of the resulted simulation

Raw files of the simulation results are not included because of their big number and size.

Pre-requirment
==============
This code is pretty simple, no specific packages are required other than the usual packages:
* Need to be installed:
  * click 
  * pandas
  * Numpy 
  * networkx
* Standard library packages:
  * json 
  * gz 

Command line interface
======================
It is a simple interface: 
```bash
$ python cli.py --help
Usage: cli.py [OPTIONS]

Options:
  --output TEXT
  --simulation_variables_file TEXT
  --simulation_duration INTEGER
  --contact_reduction_day INTEGER
  --relaxation INTEGER
  --help                          Show this message and exit.
```

Example:
```
$ python cli.py --output "test.json.gz" --simulation_variables_file three_percent_loose_sv.txt --simulation_duration 20 --contact_reduction_day 10
```