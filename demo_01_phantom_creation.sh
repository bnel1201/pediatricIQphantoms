# PHANTOM PARAMETERS
phantom=anthropomorphic # <-- current options include [CCT189, CTP404, anthropomorphic]
patient_diameters=200
reference_diameter=200 # <-- diameter in mm of the real physcial phantom for comparison
reference_fov=340 # <-- FOV in mm of adult protocol used in scanning real physical phantom for comparison

# CT SIMULATION PARAMETERS
framework=MIRT
nsims=10 # <-- number of simulations to perform with different noise instantiations
image_matrix_size=512 # <-- reconstructed matrix size in pixels (square, equal on both sides)
nangles=580 # <-- number of angular projections in the CT acquisition (currently only axial scans are supported)

aec_on=true # (aec built in to ped xcat) <-- 'aec' = automatic exposure control, when `true`, it ensures constant noise levels for all `patient_diameters` (see `reference_dose_level` for more info)
add_noise=true # <-- if true adds Poisson noise, noise magnitude set by `reference_dose_level`, noise texture set by reconstructed field of view (cuttently fov = 110% patient_diameter) 
reference_dose_level='3e5*[10 25 40 55 70 85 100]/100' # <-- units of photons, this expression is evaluated by matlab, so keep in this format '[xx, yy, zz]'
offset=0 # <-- CT number of water. Note: some DLIR models were trained with offset=0 or 1000, so this parameter should match the model training conditions

# -----------------------
