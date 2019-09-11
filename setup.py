# -*- coding: utf-8 -*-
import sys

#from distutils.core import setup
from setuptools import setup

long_description='''\
Overview
========

This package can be used to record data from a Tektronix MSO4/5/6 connected as TCPIP instrument. 


Installation
============

You need first to install the `PyVISA`_ package. 
To install pyTekMSO, download the package and run the command:

  python setup.py install

You can also directly move the pyTekMSO directory to a location
that Python can import from (directory in which scripts 
using PyDAQmx are run, etc.)

Sources can also be download on the `pyTekMSO github repository`_. 

Usage
=====

Example usage::

  from pyTekMSO import TekMSO

  ACQ_N = 5
  scope = TekMSO(<IP address>)
  scope.set_fastframe_count_to_max()
  for i in range(ACQ_N):
    scope.enable_fastframe()
    scope.enable_save_on_trigger()
    scope.start_sequence_acq()
    # Run application here

    # END Run application here
    while scope.get_acq_state() != 0:
        pass
    pass

Contact
=======

Please send bug reports or feedback to `Thore Tiemann`_.

Version history
===============
Main changes:

* 0.1 Initial relase

.. _Thore Tiemann: mailto:thore.tiemann@student.uni-luebeck.de
.. _pyTekMSO github repository: https://github.com/lamermoon/pyTekMSO
.. _PyVISA: http://pyvisa.sourceforge.net/
'''


setup(name="pyTekMSO", version='0.1',
      author='Thore Tiemann', author_email="thore.tiemann@student.uni-luebeck.de",
      maintainer='Thore Tiemann',
      maintainer_email="Thore Tiemann",
      url='https://github.com/lamermoon/pyTekMSO',
      license="MIT",
      description='TCPIP interface to Tektronix Scope',
      long_description = long_description,  
      requires=['pyvisa'],
      packages=["pyTekMSO"]
)
