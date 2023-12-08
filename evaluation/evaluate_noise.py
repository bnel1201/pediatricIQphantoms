import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import SimpleITK as sitk


def clean_dataframe(df):
    clean_df = df.copy()
    clean_df = clean_df[clean_df['diameter [mm]'] != 200]
    clean_df.replace('hanning205', 'sharp', regex=True, inplace=True)
    clean_df.replace('hanning085', 'smooth', regex=True, inplace=True)
    clean_df.replace('_', ' ', regex=True, inplace=True)
    clean_df['dose level [%]'] = (clean_df['dose']/clean_df['dose'].max()*100).astype(int)
    return clean_df


def main(data_dir, outfile=None):
    img_file = list(Path(data_dir).rglob('*/bkg/*.mhd'))

    filenames = []
    phantom_diameter_mm = []
    recon = []
    dose_photons = []
    sample_mean = []
    sample_std = []

    for imgf in img_file:
        if imgf.stem.startswith('true'): continue

        dose = int(imgf.parents[1].stem.split('_')[1])
        diameter = int(imgf.parents[2].stem.split('diameter')[-1].split('mm')[0])
        recon_kernel = imgf.parents[3].stem

        vol = sitk.GetArrayFromImage(sitk.ReadImage(imgf))
        _, nx, ny = vol.shape
        for np_img in vol:

            std = np_img[nx//2-nx//4:nx//2+nx//4, ny//2-ny//4:ny//2+ny//4].std()
            mean = np_img[nx//2-nx//4:nx//2+nx//4, ny//2-ny//4:ny//2+ny//4].mean()

            filenames.append(str(imgf))
            phantom_diameter_mm.append(diameter)
            recon.append(recon_kernel)
            sample_std.append(std)
            sample_mean.append(mean)
            dose_photons.append(dose)

    df = pd.DataFrame({'recon': recon,
                    'diameter [mm]': phantom_diameter_mm,
                    'dose': dose_photons,
                    'mean [HU]': sample_mean,
                    'noise std [HU]': sample_std,
                    'filename': filenames})

    df = clean_dataframe(df)

    denoised = df[df['recon'] != 'fbp sharp'].reset_index(drop=True)
    fbp = df[df['recon'] == 'fbp sharp'].reset_index(drop=True)
    denoised['noise reduction [%]'] = (fbp['noise std [HU]'] - denoised['noise std [HU]'])/fbp['noise std [HU]']*100

    f, axs = plt.subplots(2,2, sharey='row', sharex='col', figsize=(8, 6), dpi=300, tight_layout=True)
    sns.lineplot(ax=axs[0, 0], data=df, x='diameter [mm]', y='noise std [HU]', style='recon', hue='dose level [%]')
    sns.lineplot(ax=axs[0, 1], data=df, x='dose level [%]', y='noise std [HU]', style='recon', hue='diameter [mm]')

    sns.lineplot(ax=axs[1, 0], data=denoised, x='diameter [mm]', y='noise reduction [%]', style='recon', hue='dose level [%]')
    sns.lineplot(ax=axs[1, 1], data=denoised, x='dose level [%]', y='noise reduction [%]', style='recon', hue='diameter [mm]')
    plt.legend(loc='lower right')

    if outfile:
        f.savefig(outfile, dpi=600, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate Noise Reduction From pediatricIQphantoms dataset')
    parser.add_argument('data_dir', help="configuration toml file containing simulation parameters")
    parser.add_argument('--outfile', '-o', default=None, help="name of image file to save output plot e.g. 'dose_size_dependence.png'")
    args = parser.parse_args()
    
    main(data_dir=args.data_dir, outfile=args.outfile)
