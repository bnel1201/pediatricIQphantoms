import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils.mtf_plot import plot_patient_diameter_mtf


def get_cutoff_val_coords(mtf_df, cutoff_val):
    val = mtf_df.iloc[(np.abs(mtf_df - cutoff_val)).argmin()]
    freq = mtf_df.index[(np.abs(mtf_df - cutoff_val)).argmin()]
    return freq, val


def plot_sample_curves(datadir, diameter, contrast, cutoff_val=None, ax=None):
    fbp_color='tab:blue'
    redcnn_color='tab:red'

    # datadir = Path('/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CTP404/monochromatic/')
    fbp_mtf_df = pd.read_csv(datadir / f'diameter{diameter}mm' / 'I0_3000000' / 'fbp_sharp_v001_mtf.csv')
    fbp_mtf_df['frequencies [lp/cm]'] = fbp_mtf_df['frequencies [1/mm]'] * 10
    fbp_mtf_df.pop('frequencies [1/mm]')
    fbp_mtf_df.set_index('frequencies [lp/cm]', inplace=True)
    fbp_mtf_df.columns = [abs(int(c.split(' HU')[0])) for c in fbp_mtf_df.columns]

    redcnn_mtf_df = pd.read_csv(datadir / f'diameter{diameter}mm' / 'I0_3000000_processed' / 'fbp_sharp_v001_mtf.csv')
    redcnn_mtf_df['frequencies [lp/cm]'] = redcnn_mtf_df['frequencies [1/mm]'] * 10
    redcnn_mtf_df.pop('frequencies [1/mm]')
    redcnn_mtf_df.set_index('frequencies [lp/cm]', inplace=True)
    redcnn_mtf_df.columns = [abs(int(c.split(' HU')[0])) for c in redcnn_mtf_df.columns]

    if ax is None:
        f, ax = plt.subplots()

    fbp_mtf_df[contrast].plot(ax=ax, label='FBP', color=fbp_color)
    redcnn_mtf_df[contrast].plot(ax=ax, label='REDCNN', color=redcnn_color)

    
    xlim = [0, 11]
    ax.hlines(y=0.5, xmin=0, xmax=xlim[1], linestyle='--', color='black')

    freq, val = get_cutoff_val_coords(fbp_mtf_df[contrast], cutoff_val/100)
    offset = 0.25

    ax.annotate('', xy=(freq-offset, 0), xycoords='data', xytext=(freq-offset, 0.5), arrowprops=dict(arrowstyle='->', color=fbp_color, linestyle='--'))
    ax.annotate(f'FBP 50% MTF\n{freq-offset:2.2f}', xy=(freq+1.6, 0.05), horizontalalignment='center')


    red_freq, val = get_cutoff_val_coords(redcnn_mtf_df[contrast], cutoff_val/100)
    ax.annotate('', xy=(red_freq-offset, 0), xycoords='data', xytext=(red_freq-offset, 0.5), arrowprops=dict(arrowstyle='->', color=redcnn_color, linestyle='--'))
    ax.annotate(f'REDCNN 50% MTF\n{red_freq-offset:2.2f}', xy=(red_freq-2.7, 0.05),  horizontalalignment='center')
    rel_sharp = red_freq/freq
    rel_sharp = f'{rel_sharp:2.3f}'[:-1]
    ax.annotate(f'Relative Sharpness\n{red_freq-offset:2.2f}/{freq-offset:2.2f}={rel_sharp}', xy=(8, 0.6),  horizontalalignment='center', bbox=dict(boxstyle='round', fc='tab:blue'), color='white')

    ax.legend()
    ax.set_ylabel('MTF')
    ax.set_xlim(xlim)
    ax.set_ylim([0, 1])


def main(datadir=None, output_fname=None, processed=False):
    datadir = datadir or '/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CTP404/monochromatic/'
    datadir = Path(datadir)
    patient_dirs = sorted(list(datadir.glob('diameter*')))

    sns.set_style("darkgrid")
    sns.set_context("talk")
    f, axs = plt.subplots(2, 3, figsize=(9, 7), sharex='col', sharey='row',
                        gridspec_kw=dict(hspace=0.1, wspace=0.1))
    for patient_dir, ax in zip(patient_dirs, axs.flatten()):
        if processed:
            mtf_csv_fname = patient_dir / 'I0_3000000_processed' / 'fbp_sharp_v001_mtf.csv'
        else:
            mtf_csv_fname = patient_dir / 'I0_3000000' / 'fbp_sharp_v001_mtf.csv'
        plot_patient_diameter_mtf(mtf_csv_fname, ax=ax)


    mtf_results_dir = Path(output_fname).parent
    mtf_results_dir.mkdir(exist_ok=True, parents=True)
    if output_fname is None:
        plt.show()
    else:
        
        f.savefig(output_fname, dpi=600)
        print(f'File saved: {output_fname}')

    diameter = int(patient_dirs[len(patient_dirs)//2].stem.split('diameter')[1].split('mm')[0])
    contrast = 35
    
    f, ax = plt.subplots(figsize=(4,4), tight_layout=True)
    plot_sample_curves(datadir, diameter, contrast, cutoff_val=50, ax=ax)
    ax.set_title(f'Patient Diameter: {diameter}mm\nContrast: {contrast}HU')
    output_fname = Path(mtf_results_dir) / 'sample_mtf_curves.png'
    f.savefig(output_fname, dpi=600, bbox_inches='tight')
    print(f'File saved: {output_fname}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots MTF Curves')
    parser.add_argument('--datadir', '-d',
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--output_fname','-o', required=False,
                        help="filename for the saved plot")
    parser.add_argument('--processed', action='store_true', default=False,
                        help='boolean to plot the processed results, defaults to false using the baseline')
    args = parser.parse_args()
    main(args.datadir, output_fname=args.output_fname, processed=args.processed)