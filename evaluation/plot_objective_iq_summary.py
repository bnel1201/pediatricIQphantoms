import argparse

import matplotlib.pyplot as plt
import seaborn as sns

from NPS.utils.csv_io import get_noise_reduction_df
from MTF.utils.csv_io import load_csv as load_mtf_csv

sns.set_style("darkgrid")
# sns.set_context("talk")

def plot_sharpness_heatmap(mtf_rel, cutoff_val=50, ax=None):
    if ax is None:
        f, ax = plt.subplots()
    mtf_rel.columns = [int(c.split('mm')[0]) for c in mtf_rel.columns]
    ax = sns.heatmap(mtf_rel.astype(float), annot=True, ax=ax,
                cbar_kws=dict(label=f'Relative Sharpness\n(REDCNN {cutoff_val}% MTF / FBP {cutoff_val}% MTF',
                location='bottom'), cmap='crest')
    ax.collections[0].colorbar.ax.invert_xaxis()
    plt.yticks(rotation=0) 
    ax.set_xlabel('Patient Diameter [mm]')


def plot_noise_reduction(noise_reduction_df, ax=None):
    if ax is None:
        f, ax = plt.subplots()
    noise_reduction_df.plot(ax=ax, ylabel='Relative Noise Reduction [%]\n$|\sigma_{REDCNN} - \sigma_{FBP}| / \sigma_{FBP}\\times 100$')
    ax.set_xlabel('')
    ax.set_xticks([])
    ax.get_legend().remove()


def main(results_dir, output_fname):

    nps_csv_fname = f'{results_dir}/NPS/diameter_summary.csv'
    noise_reduction_df = get_noise_reduction_df(nps_csv_fname)

    mtf50_rel, mtf10_rel = load_mtf_csv(f'{results_dir}/MTF/relative_sharpness_values.csv')
    mtf50_rel.pop('%MTF cutoff')
    mtf50_rel.set_index('Contrast [HU]', inplace=True)

    fig = plt.figure(figsize=(5, 8), constrained_layout=False)
    l, r = 0.2, 0.99
    gs1 = fig.add_gridspec(1, 1, left=l, right=r, top = 0.59, bottom=0.05)
    main_ax = fig.add_subplot(gs1[0])
    plot_sharpness_heatmap(mtf50_rel, cutoff_val=50, ax=main_ax)

    gs2 = fig.add_gridspec(1, 1, left=l, right=r, top = 0.99, bottom=0.6)
    sub_ax = fig.add_subplot(gs2[0])
    plot_noise_reduction(noise_reduction_df, ax=sub_ax)
    if output_fname is None:
        plt.show()
    else:
        fig.savefig(output_fname, dpi=600)
        print(f'File saved: {output_fname}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots objective image quality summary figure')
    parser.add_argument('--results_dir', '-d',
                        help="directory containing MTF and NPS results")
    parser.add_argument('--output_fname', '-o',
                        help="filename for the saved plot")
    args = parser.parse_args()
    main(args.results_dir, output_fname=args.output_fname)
