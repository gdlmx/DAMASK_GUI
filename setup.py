#!/usr/bin/env python
# -*- coding: utf-8
from sys import version_info

from io import open
from setuptools import setup, find_packages

setup(
    name='damask_gui',
    version='0.1.0',
    description='GUI for Düsseldorf Advanced Material Simulation Kit',
    #long_description = long_description,
    author='Mingxuan Lin',
    author_email='mingxuan.lin@iehk.rwth-aachen.de',
    license='MIT',
    packages=['damask_gui','damask_gui.plugin'],
    requires=['PyQt4', 'matplotlib', 'parsimonious'],
    #package_data={'damask_gui': ['*.pyc','*.pyo']},
    #tests_require=[],
    #test_suite='',
    url='',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: End Users',
        'Natural Language :: English',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities'],
    keywords=['DAMASK', 'Visualization', 'RVE', 'Crystal Plasticity'],
    use_2to3=version_info >= (3,)
)
