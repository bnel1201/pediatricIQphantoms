# %%
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import SimpleITK as sitk
# %%

data_dir = Path('/home/brandon.nelson/Dev/Regulatory_Science_Tools/pediatricIQphantoms/main/images/CCT189/')

# %%
img_file = list(data_dir.rglob('*/bkg/*.mhd'))
# %%

filenames = []
phantom_diameter_mm = []
fov_size_mm =[]
pixel_size_mm = []
recon = []
dose_photons = []
sample_mean = []
sample_std = []
nps_peak_cyc_per_pix = []
nps_mean = []
nps_std = []
rmse = []


for imgf in img_file:
    if imgf.stem.startswith('true'): continue

    dose = int(imgf.parents[1].stem.split('_')[1])
    diameter = int(imgf.parents[2].stem.split('diameter')[-1].split('mm')[0])
    recon_kernel = imgf.parents[3].stem
    phantom =  imgf.parents[4].stem

    img = sitk.ReadImage(imgf)
    nx, ny, nz = img.GetSize()
    
    np_img = sitk.GetArrayFromImage(img)

    for slice_idx in range(nz):

        std = np_img[nx//2-nx//4:nx//2+nx//4, nx//2-nx//4:nx//2+nx//4, slice_idx].std()
        mean = np_img[nx//2-nx//4:nx//2+nx//4, nx//2-nx//4:nx//2+nx//4, slice_idx].mean()

        filenames.append(str(imgf))
        phantom_diameter_mm.append(diameter)
        recon.append(recon_kernel)
        sample_std.append(std)
        sample_mean.append(mean)
        dose_photons.append(dose)

df = pd.DataFrame({'recon': recon, 'diameter_mm': phantom_diameter_mm, 'dose': dose_photons, 'mean': sample_mean, 'std': sample_std, 'filename': filenames})
# %%
df = df[df['diameter_mm'] != 200]
# %%
sns.lineplot(data=df, x='diameter_mm', y='std', style='recon', hue='dose')
# %%
denoised = df[df['recon'] != 'fbp_hanning205'].reset_index(drop=True)
# %%
fbp = df[df['recon'] == 'fbp_hanning205'].reset_index(drop=True)
# %%
denoised['noise reduction [%]'] = (fbp['std'] - denoised['std'])/fbp['std']*100
denoised
# %%
sns.lineplot(data=denoised, x='diameter_mm', y='noise reduction [%]', style='recon', hue='dose')
# %%
sns.lineplot(data=denoised, x='dose', y='noise reduction [%]', style='recon', hue='diameter_mm')

# %%
