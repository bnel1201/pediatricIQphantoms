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

Examples
--------

- `example_01_multiple_recon_kernels.sh <https://github.com/bnel1201/pediatricIQphantoms/blob/main/demo_01_phantom_creation.sh>`_

.. code-block:: shell

    python make_phantoms.py configs/multiple_recon_kernels.toml

The key difference here is in the config file

.. code-block:: toml

    [[simulation]]

    model = ['CCT189'] 
    diameter = [112, 131, 151, 185, 200, 292, 350] 

    ...

    fbp_kernel = 'hanning,2.05'

    [[simulation]]

    fbp_kernel = 'hanning,0.85'

    [[simulation]]

    model = ['CTP404']
    dose_level = [1.0]
    fbp_kernel = 'hanning,2.05'

    [[simulation]]

    fbp_kernel = 'hanning,0.85'
   ...

Here multiple simulations are run, note the repeated header blocks `[[simulation]]` indicate the start of a new experiment. Any parameters set in the first simulation, (the first `[[simulation]]` above), override the `default parameters <defaults.toml>`_. In each subsequent `[[simulation]]` an new provided settings will update the scan settings, otherwise all other parameters will carry over from the previous simulation.

For example:

.. code-block:: python

    {'image_directory': 'results/multiple_recon_kernels',
    'model': ['CCT189'],
    'diameter': [112, 131, 151, 185, 200, 292, 350],
    'reference_diameter': 200,
    'framework': 'MIRT',
    'nsims': 200,
    'nangles': 1160,
    'aec_on': True,
    'add_noise': True,
    'full_dose': 300000.0,
    'dose_level': [0.1, 0.25, 1.0],
    'sid': 595,
    'sdd': 1085.6,
    'nb': 880,
    'na': 1160,
    'ds': 1,
    'offset_s': 1.25,
    'fov': 340,
    'image_matrix_size': 512,
    'offset': 0,
    'fbp_kernel': 'hanning,2.05'}

In the second simulation in the config file only the `fbp_kernel` is updated 

.. code-block:: toml

    [[simulation]]

    fbp_kernel = 'hanning,0.85'

This results in only updating the `fbp_kernel` element leaving all other elements the same from the previous simulation.

.. code-block:: python

    {'image_directory': 'results/multiple_recon_kernels',
     'model': ['CCT189'],
     'diameter': [112, 131, 151, 185, 200, 292, 350],
     'reference_diameter': 200,
     'framework': 'MIRT',
     'nsims': 200,
     'nangles': 1160,
     'aec_on': True,
     'add_noise': True,
     'full_dose': 300000.0, 
     'dose_level': [0.1, 0.25, 1.0],
     'sid': 595,
     'sdd': 1085.6,
     'nb': 880,
     'na': 1160,
     'ds': 1,
     'offset_s': 1.25,
     'fov': 340,
     'image_matrix_size': 512,
     'offset': 0,
     **'fbp_kernel': 'hanning,0.85'**}

Then by third simulation a new phantom is introduced, CTP404, and we wish to only image it at full dose and with the first of the two kernels being investigated (sharp and smooth):

.. code-block:: toml

    [[simulation]]

    model = ['CTP404']
    dose_level = [1.0]
    fbp_kernel = 'hanning,2.05'

.. code-block:: python

    {'image_directory': 'results/multiple_recon_kernels',
     **'model': ['CTP404']**,
     'diameter': [112, 131, 151, 185, 200, 292, 350],
     'reference_diameter': 200,
     'framework': 'MIRT',
     'nsims': 10,
     'nangles': 1160,
     'aec_on': True,
     'add_noise': True,
     'full_dose': 3000000.0,
     **'dose_level': [1.0]**,
     'sid': 595,
     'sdd': 1085.6,
     'nb': 880,
     'na': 1160,
     'ds': 1,
     'offset_s': 1.25,
     'fov': 340,
     'image_matrix_size': 512,
     'offset': 0,
     'fbp_kernel': 'hanning,2.05'}

Finally by the fourth we repeat the previous simulation but with the second kernel, the smooth kernel

.. code-block:: toml

    [[simulation]]

    fbp_kernel = 'hanning,0.85'

.. code-block:: python

    {'image_directory': 'results/multiple_recon_kernels',
     **'model': ['CTP404']**,
     'diameter': [112, 131, 151, 185, 200, 292, 350],
     'reference_diameter': 200,
     'framework': 'MIRT',
     'nsims': 10,
     'nangles': 1160,
     'aec_on': True,
     'add_noise': True,
     'full_dose': 3000000.0,
     'dose_level': [1.0],
     'sid': 595,
     'sdd': 1085.6,
     'nb': 880,
     'na': 1160,
     'ds': 1,
     'offset_s': 1.25,
     'fov': 340,
     'image_matrix_size': 512,
     'offset': 0,
     **'fbp_kernel': 'hanning,0.85'**}

This is done in parsing the config files using the python `dict update method <https://docs.python.org/3/library/stdtypes.html?highlight=dict%20update#dict.update>`_ https://github.com/bnel1201/pediatricIQphantoms/blob/62a45930053502e8e9982af4b521fdd4eee314ed/make_phantoms.py#L56

[1] Nelson B, Kc P, Badal-Soler A, Jiang L, Masters S, Zeng R. Pediatric-Specific Evaluations for Deep Learning CT Denoising. Published online July 3, 2023. doi:10.5281/zenodo.8111530
[2] Zeng R, Lin CY, Li Q, et al. Performance of a deep learning-based CT image denoising method: Generalizability over dose, reconstruction kernel, and slice thickness. Med Phys. 2022;49(2):836-853. doi:10.1002/mp.15430

