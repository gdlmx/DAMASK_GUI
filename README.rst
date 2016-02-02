==========
DAMASK_GUI
==========

DAMASK_GUI aims to provide an easy-to-use graphical user interface for DAMASK while keeping maximum compatibility with the existing command line interface.

Install
=======

.. code:: sh

    $ python setup.py install

Example Usage
=============

To start the main window:

.. code:: bash

    $ python -m damask_gui

To directly run a script in command line:

.. code:: bash

    $ python -m damask_gui.plugin.D3DReader [options]


How it works
============

DAMASK_GUI uses the pipe line concept, where a pre/post-processing step is implemented in a pipeline-element (called ``filter``). It mimic the widely-used ``optparse`` package, so that, every ``optparse-based`` script can be easily transformed into a filter.

