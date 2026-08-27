=====================
Red Pitaya JupyterLab
=====================

Example notebooks and Python drivers for controlling a Red Pitaya board from
JupyterLab running on the board itself.

JupyterLab is part of the Red Pitaya OS image. The notebooks live in
``/home/jupyter``, the server is started by ``jupyter.service`` and is served on
port 8888 under the ``/jlab`` base URL, so a board is reached at
``http://<board-address>:8888/jlab``. Open ``welcome.ipynb`` first.

Repository layout
=================

``examples/``
    Notebooks for the current API, grouped by topic: ``analog``, ``digital``,
    ``acquisition``, ``generation``, ``acquisition_generation``, ``dma``,
    ``hardware``, ``multiboard_sync`` and ``click_shield_examples``.
    ``examples/outdated/`` keeps the notebooks written for the older Mercury
    API.

``experiments/``
    Low level notebooks: AXI4-Lite GPIO, XADC, classic FPGA monitor and
    oscilloscope filter. They are built on the deprecated Mercury layer.

``redpitaya/``
    The ``redpitaya`` Python package installed from this repository. It is the
    deprecated Mercury layer, see below. ``drv/`` holds register level drivers
    for the Mercury FPGA image (through ``/dev/uio`` and ``mmap``),
    ``overlay/`` loads the FPGA overlay and ``app/`` contains two Bokeh based
    applications, an oscilloscope and a signal generator.

``docs/``
    Sphinx configuration used to build the documentation.

``welcome.ipynb``
    Tutorial entry point.

Python API
==========

The current examples use the SWIG bindings of the C API. They are shipped with
the ecosystem, not with this repository:

.. code-block:: python

    from rp_overlay import overlay
    import rp

    fpga = overlay()
    rp.rp_Init()

``rp`` and ``rp_overlay`` are installed in ``/opt/redpitaya/lib/python``. The
``Python 3 (RP api)`` kernel adds that directory to ``PYTHONPATH``, so select
that kernel when running the examples.

Deprecated Mercury layer
========================

.. code-block:: python

    from redpitaya.overlay.mercury import mercury as overlay

    fpga = overlay()

``redpitaya.overlay.mercury`` is no longer supported and will be removed in a
future release. Do not write new code against it. It requires the Mercury FPGA
image, which current OS versions do not use.

What still depends on it: the notebooks in ``examples/outdated/`` and
``experiments/``, and both Bokeh applications in ``redpitaya/app/``, which
import the layer directly.

Use the Python API shown above instead. It matches the C API command by
command, so the documentation of the C API applies to it as well.

OS history
==========

- OS 2.00-18 and older use a modified FPGA image called Mercury. The notebook
  commands come from the ``redpitaya`` package in this repository.
- OS 2.00-23 and newer use the standard Red Pitaya FPGA image. The notebook
  commands are the same as the C and Python API commands and run the
  corresponding C API functions in the background.

Installation
============

The Python API needs no installation from here, it comes with the ecosystem.
The ``redpitaya`` package of this repository, the deprecated Mercury layer, is
installed by the OS image build: the repository is cloned to
``/home/jupyter/RedPitaya`` and installed in editable mode.

To install it by hand, on the board or on a development machine:

.. code-block:: console

    pip install -e .

The drivers in ``redpitaya/drv`` need ``/dev/uio`` devices, so they only work on
the board itself.

Dependencies
============

``install_requires`` in ``setup.py`` pins the exact versions of ``numpy``,
``scipy``, ``bokeh``, ``IPython`` and ``ipywidgets`` that the OS image ships.
Those pins have to stay in sync with the Python stage of the OS image build:
when they diverge, installing this package on a board either downgrades the
image stack or leaves an unsatisfied requirement behind.

Documentation
=============

Official documentation: https://redpitaya.readthedocs.io

The JupyterLab chapter:
https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/jupyter/Jupyter.html

License
=======

GNU General Public License v3.0, see ``LICENSE``.
