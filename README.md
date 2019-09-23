# pyTekMSO

## Overview
This package was tested with Python 3.7 and can be used to communicate with a Tektronix MSO4/5/6 oscilloscope.

Currently only basic actions are supported such as
- starting a measurement
- checking whether a measurement has finished
- configure and activate FastFrame

## Installation
This package can be installed by running
```
python setup.py install
```
All dependent packages should be installed automatically. If that does not happen, install `pyvisa-py` and `pyvisa` using either `pip3` or your packet manager.

[PyVISA Documentation](https://pyvisa.readthedocs.io/en/latest/index.html)
