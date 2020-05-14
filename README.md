The impact of community containment implementation timing on the spread of COVID-19: A simulation study
===================================================
Attayeb Mohsen and Ahmed Alarabi
---

This repository is the companion for the paper submitted to F1000Research

Repository files
================
* simulation.py: The main simulation code
* cli.py: Command line interface

Pre-requirment
==============
This code is pretty simple, no specific packages are required other than the usual packages:
* Need to be installed:
  * click [Need to be installed]
  * pandas [Need to be installed]
  * Numpy [Need to be installed]
* Standard library packages:
  * json [Standard library package]
  * gz [standard library package]

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