import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

from utils.csv_io import append_adult_data_to_mtf_cutoff_data


def plot_sharpness_heatmap(mtf_rel, cutoff_val, results_dir=None, ax=None):

    mtf_rel.columns = [int(c.split('mm')[0]) for c in mtf_rel.columns]
    mtf_rel.sort_index(ascending=False, inplace=True)
    if ax is None:
        f, ax = plt.subplots()
    sns.heatmap(mtf_rel, annot=True, ax=ax,
                cbar_kws=dict(label=f'Relative Sharpness\n(REDCNN {cutoff_val}% MTF / FBP {cutoff_val}% MTF'), cmap='crest')
    ax.set_xlabel('Patient Diameter [mm]')
    twiny = ax.twiny()

    fovs = np.round(mtf_rel.columns*1.1).astype(int).to_list()
    fovs[mtf_rel.columns.to_list().index(150)] = 340 # From RZ, min FOV for adult scan protocol
    twiny.set_xticks(ax.get_xticks(), fovs)
    twiny.set_xlim(ax.get_xlim())
    twiny.set_xlabel("Recon FOV [mm]")
    nrows = len(mtf_rel)
    rect = patches.Rectangle((6, 0.05), 0.97, nrows-0.1, linewidth=3, edgecolor='tab:blue', facecolor='none')
    ax.annotate("Adult Reference",
                xy=(6.75, nrows), xycoords='data',
                xytext=(0.75, 0.025), textcoords='figure fraction',
                color='tab:blue',
                arrowprops=dict(facecolor='tab:blue', shrink=0.05), weight='bold')
    ax.add_patch(rect)

    if results_dir:
        output_fname = Path(results_dir) / f'mtf{cutoff_val}_sharpness_heatmap.png'
        f.savefig(output_fname, dpi=600)
        print(f'File saved: {output_fname}')


def main(mtf_results_dir, cutoff_val=50, contrasts=None):

    contrasts = contrasts or [15, 35, 120, 200, 340, 990, 1000]

    fbp_data, redcnn_data = append_adult_data_to_mtf_cutoff_data(mtf_results_dir, 50)
    mtf50_rel = redcnn_data / fbp_data
    mtf50_rel = mtf50_rel[mtf50_rel.index.isin(contrasts)]
    f, ax = plt.subplots()
    plot_sharpness_heatmap(mtf50_rel, cutoff_val=cutoff_val, results_dir=None, ax=ax)
    output_fname = Path(mtf_results_dir) / 'plots/mtf50_relative_sharpness.png'
    f.savefig(output_fname, dpi=600)

    print(f'File saved: {output_fname}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots MTF cutoff curves')
    parser.add_argument('--datadir', '-d',
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--contrasts', '-c', nargs='+',
                        help="Contrast disks to include [list of integers: -1000, 15, 35, 120, 340, 990]")
    args = parser.parse_args()
    contrasts = list(map(int, args.contrasts[0].split(' '))) if args.contrasts else None
    main(args.datadir, contrasts=contrasts)
