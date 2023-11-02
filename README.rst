pediatricIQphantoms
===================
Digital Pediatric Image Quality Phantoms for Evaluating CT Denoising Methods

Please visit our Zenodo page to download the full dataset:

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.10064036.svg
  :target: https://doi.org/10.5281/zenodo.10064036

The set of Digital Phantoms for Pediatric CT Performance Assessment consists of analytical quality assurance phantom models and interfaces to CT simulation frameworks to generate simulated CT images representing different diameters of each phantom.

The phantoms incude:

1. The CTP404 contrast module phantom for assessing CT number accuracy and contrast-dependent spatial resolution
2. CCT189 the MITA LCD phantom for assessing low contrast detectability
3. Uniform water phantoms for assessing noise and noise texture

In addition, this repo contains examples of measurements using these digital image quality phantoms

1. phantom creation and simulation, including different scanner configurations and acquisition protocols
2. noise and noise texture measurements
3. sharpness measurements
4. low contrast detectability measurements using [lcd-ct](https://github.com/DIDSR/LCD_CT)

.. image:: ped_dl_eval_tool.png
        :width: 800
        :align: center

Contribute
----------

- Issue Tracker: https://github.com/DIDSR/LCD_CT/issues
- Source Code: https://github.com/DIDSR/LCD_CT
- Contributing Guide: https://lcd-ct.readthedocs.io/en/latest/contributing.html

Support
-------

If you are having issues, please let us know.
brandon.nelson@fda.hhs.gov; rongping.zeng@fda.hhs.gov

License
-------

The project is licensed under `Creative Commons Zero v1.0 Universal LICENSE`_.

Disclaimer
--------
This software and documentation (the "Software") were developed at the Food and Drug Administration (FDA) by employees of the Federal Government in the course of their official duties. Pursuant to Title 17, Section 105 of the United States Code, this work is not subject to copyright protection and is in the public domain. Permission is hereby granted, free of charge, to any person obtaining a copy of the Software, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, or sell copies of the Software or derivatives, and to permit persons to whom the Software is furnished to do so. FDA assumes no responsibility whatsoever for use by other parties of the Software, its source code, documentation or compiled executables, and makes no guarantees, expressed or implied, about its quality, reliability, or any other characteristic. Further, use of this code in no way implies endorsement by the FDA or confers any advantage in regulatory decisions. Although this software can be redistributed and/or modified freely, we ask that any derivative works bear some notice that they are derived from it, and any modified versions bear some notice that they have been modified.