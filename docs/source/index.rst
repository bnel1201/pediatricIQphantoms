Welcome to pediatricIphantom documentation!
===========================================

This documentation provides information regarding how to download, install, and use the pediatricIQphantoms tools which are designed sim.

Introduction
------------

|zenodo| |tests|

.. image:: ped_dl_eval_tool.png
        :width: 800
        :align: center

.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.10064035.svg
    :alt: Zenodo Data Access
    :target: https://zenodo.org/doi/10.5281/zenodo.10064035

.. |tests| image:: https://github.com/bnel1201/pediatricIQphantoms/actions/workflows/python-package-conda.yml/badge.svg?branch=main
    :alt: Package Build and Testing Status
    :target: https://github.com/bnel1201/pediatricIQphantoms

**Digital Pediatric Image Quality Phantoms for Evaluating CT Denoising Methods** are a set of digital phantoms and simulation methods for generating CT images of standard image quality (IQ) phantoms designed to match the effective diameter of pediatric patients ranging from newborns to teenagers. This repository has `tools <make_phantoms.py>`_ for generating `MITA-LCD phantom <https://www.phantomlab.com/catphan-mita>`_ and a multi-contrast sensitometry module similar to the CTP404 module of the `Catphan 600 phantom <link here>`_. Functions are also provided to simulate different acquisition parameters and CT scanner models.

Size is one of the most important patient factors influencing CT performance as it determines the overall x-ray attenuation and noise properties. New deep learning-based denoisers have shown potential to improve image quality for a fixed radiation dose or maintain image quality while reducing dose <cite>.  Performance Assessment consists of analytical quality assurance phantom models and interfaces to CT simulation frameworks to generate simulated CT images representing different diameters of each phantom.

Installation
------------

*Installation is only required to generate new datasets*, a pregenerated dataset can be downloaded from `Zenodo <https://zenodo.org/doi/10.5281/zenodo.10064035>`_, only proceed if you want to generate new simulated datasets.

.. _version requirements:

**Requirements**

- `Conda <https://docs.conda.io/projects/conda/en/stable/user-guide/getting-started.html>`_ package manager e.g. `Miniconda <https://docs.anaconda.com/free/miniconda/>`_

- Mac, Linux, or `Windows Subsystem for Linux (WSL) <https://learn.microsoft.com/en-us/windows/wsl/install>`_ operating systems described on the `Octave Conda Forge page <https://anaconda.org/conda-forge/octave>`_. This package currently uses the Octave-based `Michigan Image Reconstruction Toolbox (MIRT) <https://github.com/JeffFessler/mirt>`_

**Installation**

.. code-block:: shell

        git clone https://github.com/bnel1201/pediatricIQphantoms
        cd pediatricIQphantoms
        conda env create --file environment.yml
        conda activate pediatricIQphantoms

The code block above does the following in 4 lines:

1. Git clones the `pediatricIQphantoms <https://github.com/bnel1201/pediatricIQphantoms>`_ repository
2. Changes the active directory to the repo
3. Creates a new conda environment called "pediatricIQphantoms"
4. Activates the conda environment. This makes the phantom creation library `pediatricIQphantoms` accessible in scripts (see `examples <https://github.com/bnel1201/pediatricIQphantoms/blob/main/notebooks/00_running_simulations.ipynb>`_) and via command line calls (see `demos <demo_01_phantom_creation.sh>`_).

**Test the Installation**

.. code-block:: shell

        pytest

This runs the [unit tests](https://github.com/bnel1201/pediatricIQphantoms/tree/main/tests) to verify that installation was successful.

Users
-----

Check out the :doc:`usage` section for detailed information on customizing dataset running_simulations.

`Computational notebooks <https://github.com/bnel1201/pediatricIQphantoms/tree/main/notebooks>`_ have also been provided to demonstrate how to use `pediatricIQphantoms dataset <https://zenodo.org/doi/10.5281/zenodo.10064035>`_ including:
  - `running CT simulations <https://github.com/bnel1201/pediatricIQphantoms/blob/main/notebooks/00_running_simulations.ipynb>`_
  - `using the dataset to assess denoising performance in pediatric subgroups <https://github.com/bnel1201/pediatricIQphantoms/blob/main/notebooks/01_pediatric_denoising_evaluation.ipynb>`_
  
Developers
----------

If you'd like to contribute to the code or documentation of this project, please check out our :doc:`contributing` page.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   notebooks/01_pediatric_denoising_evaluation
   api
   contributing
   faq

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
