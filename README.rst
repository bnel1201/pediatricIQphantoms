pediatricIQphantoms
===================

|zenodo| |docs|

**Digital Pediatric Image Quality Phantoms for Evaluating CT Denoising Methods** are a set of digital phantoms and simulation methods for generating CT images of standard image quality (IQ) phantoms designed to match the effective diameter of pediatric patients ranging from newborns to teenagers. This repository has `tools <make_phantoms.py>`_ for generating `MITA-LCD phantom <https://www.phantomlab.com/catphan-mita>`_ and a multi-contrast sensitometry module similar to the CTP404 module of the `Catphan 600 phantom <link here>`_. Functions are also provided to simulate different acquisition parameters and CT scanner models.

.. Size is one of the most important patient factors influencing CT performance as it determines the overall x-ray attenuation and noise properties. New deep learning-based denoisers have shown potential to improve image quality for a fixed radiation dose or maintain image quality while reducing dose <cite>.  Performance Assessment consists of analytical quality assurance phantom models and interfaces to CT simulation frameworks to generate simulated CT images representing different diameters of each phantom.

.. image:: ped_dl_eval_tool.png
        :width: 800
        :align: center


.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.10064036.svg
    :alt: Zenodo Data Access
    :scale: 100%
    :target: https://doi.org/10.5281/zenodo.10064036

.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://pediatriciqphantoms.readthedocs.io/en/latest/

Features
--------

- The CTP404 contrast module phantom for assessing CT number accuracy and contrast-dependent spatial resolution
- CCT189 the MITA LCD phantom for assessing low contrast detectability
- Uniform water phantoms for assessing noise and noise texture

In addition, this repo contains examples of measurements using these digital image quality phantoms

- `phantom creation and simulation<demo_01_phantom_creation.sh>`_, including different scanner configurations and acquisition protocols
- `noise and noise texture measurements <demo_02_noise_measurements.sh>`_ 

Start Here
----------

.. _version requirements:

**Requirements** (Confirm if needed)

- Matlab (**version > R2016a**) *or* Octave (**version > 4.4**)
- If the above Matlab or Octave requirements are not met, then `conda <https://conda.io/projects/conda/en/latest/user-guide/install/index.html>`_ is required to install Octave using the `installation`_ instructions.

If required versions of Matlab or Octave are not available on your system (see how to get `matlab version <https://www.mathworks.com/help/matlab/ref/version.html>`_ or `octave version <https://docs.octave.org/v4.4.0/System-Information.html#XREFversion>`_) then see `installation`_ for how to setup an Octave environment to run LCD-CT.

.. _installation:

**Installation**

1. Git clone the LCD-CT Toolbox repository:

.. code-block:: shell

    git clone https://github.com/bnel1201/pediatricIQphantoms
    cd pediatricIQphantoms

2. *If neither Matlab or Octave are installed or do not meet the `version requirements`_, you can source `install.sh` to prepare a `conda <https://conda.io/projects/conda/en/latest/user-guide/install/index.html>`_ environment. Note: this can take about 10 minutes to complete.

.. code-block:: shell

        source install.sh

*Expected run time: 10-30 min*

3. Test the installation

...

How to Use this repo and the Pediatric IQ Phantoms
--------------------------------------------------

Contribute
----------

`Issue Tracker <https://github.com/bnel1201/pediatricIQphantoms/issues>`_ | `Source Code <https://github.com/bnel1201/pediatricIQphantoms>`_ | 

Support
-------

If you are having issues, please let us know.
brandon.nelson@fda.hhs.gov; rongping.zeng@fda.hhs.gov

Disclaimer
----------
This software and documentation (the "Software") were developed at the Food and Drug Administration (FDA) by employees of the Federal Government in the course of their official duties. Pursuant to Title 17, Section 105 of the United States Code, this work is not subject to copyright protection and is in the public domain. Permission is hereby granted, free of charge, to any person obtaining a copy of the Software, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, or sell copies of the Software or derivatives, and to permit persons to whom the Software is furnished to do so. FDA assumes no responsibility whatsoever for use by other parties of the Software, its source code, documentation or compiled executables, and makes no guarantees, expressed or implied, about its quality, reliability, or any other characteristic. Further, use of this code in no way implies endorsement by the FDA or confers any advantage in regulatory decisions. Although this software can be redistributed and/or modified freely, we ask that any derivative works bear some notice that they are derived from it, and any modified versions bear some notice that they have been modified.

License
-------

The project is licensed under `Creative Commons Zero v1.0 Universal LICENSE`_.

Additional Resources
--------------------

- https://github.com/DIDSR/LCD_CT
