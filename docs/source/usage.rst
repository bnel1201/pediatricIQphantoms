Usage
=====

Intended Purpose
----------------

The pediatricIQphantom phantom generation and CT simulation tool is intended for evaluating the patient size dependence of nonlinear, data-driven image denoising and processing algorithms by providing digital versions of standard image quality phantoms, the `MITA-LCD phantom <https://www.phantomlab.com/catphan-mita>`_ and CTP404 module of the `Catphan 600 phantom <https://www.phantomlab.com/catphan-600>`_. Evaluating the patient size dependence of denoising algorithms is important when considering the performance of these devices in pediatric populations[1]. This is due to the smaller fields of view (FOV) associated with pediatric protocols which alters the image texture, an important factor when training and testing data-drive denoising methods.

Intended users are CT device developers and  image denoising and processing software developers. Advanced nonlinear CT image reconstruction and denoising methods (products code JAK_, QIH_, LLZ_ among others) includes statistically iterative, model-based iterative and deep learning-based image reconstruction and denoising methods.

.. _JAK: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id=5631

.. _QIH: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id=5704

.. _LLZ: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id=5654

The LCD performance obtained using the LCD-CT tools can help the assessment of image quality imprvoment and quantitative dose reduction potential of advanced nonlinear CT image reconstruction and denoising methods with respect to a reference reconstruction option such as the FBP method. 

[1] Nelson B, Kc P, Badal-Soler A, Jiang L, Masters S, Zeng R. Pediatric-Specific Evaluations for Deep Learning CT Denoising. Published online July 3, 2023. doi:10.5281/zenodo.8111530
[2] Zeng R, Lin CY, Li Q, et al. Performance of a deep learning-based CT image denoising method: Generalizability over dose, reconstruction kernel, and slice thickness. Med Phys. 2022;49(2):836-853. doi:10.1002/mp.15430


.. autoscript:: demo_01_singlerecon_LCD.m

.. autoscript:: demo_02_tworecon_LCD.m

.. autoscript:: demo_03_tworecon_dosecurve_LCD.m

.. image:: https://sandbox.zenodo.org/badge/DOI/10.5072/zenodo.1150650.svg
   :target: https://sandbox.zenodo.org/record/1150650
