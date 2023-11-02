import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from utils.csv_io import (get_stats_df,
                          write_results_to_csv,
                          load_csv,
                          write_1D_nps_results_to_csv,
                          get_noise_reduction_df)
from utils.nps_plot import plot_1D_nps

DOSELEVEL = 'I0_0300000'

sns.set_style("darkgrid")
# sns.set_context("talk")
ref_diam = 200

def plot_1D_nps_all_diams(datadir, output_fname=None, **subplots_kwargs):
    diam_dirs = sorted(list(datadir.glob('diameter*')))
    diam_dirs.pop(diam_dirs.index(datadir/f'diameter{ref_diam}mm'))
    n_rows = len(diam_dirs) // 3
    f, axs = plt.subplots(n_rows, 3, dpi=300, **subplots_kwargs)
    for ax, patient_dir in zip(axs.flatten(), diam_dirs):
        fbp_dir = patient_dir / DOSELEVEL / 'NPS'
        proc_dir = patient_dir / (DOSELEVEL + '_processed') / 'NPS'
        diam = fbp_dir.parents[1].stem
        plot_1D_nps(fbp_dir, proc_dir, fig=f, ax=ax)
        ax.set_title(f'{diam}')
    [ax.get_legend().remove() for ax, d in zip(axs.flatten()[1:], diam_dirs) if ax.get_legend()]
    f.tight_layout()
    if output_fname:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        f.savefig(output_fname, dpi=600)


def make_summary_df(fbp_stats_df, proc_stats_df):
    return pd.DataFrame({'Series': ['FBP', 'REDCNN'],
                         'noise mean [ROI std in HU]': [fbp_stats_df[' std [HU]'].mean(), proc_stats_df[' std [HU]'].mean()],
                         'noise std [ROI std in HU]': [fbp_stats_df[' std [HU]'].std(), proc_stats_df[' std [HU]'].std()]})

def plot_noise_summary(fbp_dir, proc_dir, fig=None, ax=None):
    fbp_stats_df = get_stats_df(fbp_dir)
    proc_stats_df = get_stats_df(proc_dir)

    noise_summary_df = make_summary_df(fbp_stats_df, proc_stats_df)

    if ax is None or fig is None:
        fig, ax = plt.subplots()
    diam = fbp_dir.parents[1].stem
    noise_summary_df.set_index('Series', inplace=True)
    noise_summary_df.plot(ax=ax, kind='bar', y='noise mean [ROI std in HU]',
                          yerr='noise std [ROI std in HU]',
                          capsize=10,
                          xlabel='',
                          ylabel='Noise level (ROI std) [HU]',
                          title=f'{diam}',
                          rot='horizontal')
    ax.get_legend().remove()
    return fig, ax


def plot_noise_curves(fbp_dir, proc_dir, fig=None, ax=None):
    fbp_stats_df = get_stats_df(fbp_dir)
    proc_stats_df = get_stats_df(proc_dir)

    if ax is None or fig is None:
        fig, ax = plt.subplots()
    diam = fbp_dir.parents[1].stem

    color='blue'
    ax.plot(fbp_stats_df[' mean [HU]'], color=color, linestyle='-', label='FBP')
    ax.plot(proc_stats_df[' mean [HU]'], color=color, linestyle='--', label='REDCNN')
    ax.tick_params(axis='y', labelcolor=color)
    ax.set_ylabel('mean [HU]', color=color)
    ax.set_title(diam)
    ax.set_ylim(990, 1060)
    axtwin = ax.twinx()
    color='red'
    axtwin.plot(fbp_stats_df[' std [HU]'], color=color)
    axtwin.plot(proc_stats_df[' std [HU]'], color=color, linestyle='--', label='REDCNN')
    axtwin.set_ylabel('std [HU]', color=color)
    axtwin.tick_params(axis='y', labelcolor=color)
    axtwin.set_ylim(8, 32)

    return fig, ax


def plot_CT_number_noise_v_diameter(fbp_summary_df, proc_summary_df, output_fname=None, **subplotkwargs):
    f, (ax0, ax1) = plt.subplots(1, 2, **subplotkwargs)
    fbp_summary_df.plot(ax=ax0, x='Patient Diameter [mm]', y='mean CT number [HU]', label='FBP',)
    proc_summary_df.plot(ax=ax0, x='Patient Diameter [mm]', y='mean CT number [HU]', label='REDCNN')
    ax0.set_ylabel('CT Number [HU]')

    fbp_summary_df.plot(ax=ax1, x='Patient Diameter [mm]', y='mean noise (ROI std) [HU]', label='FBP')
    proc_summary_df.plot(ax=ax1, x='Patient Diameter [mm]', y='mean noise (ROI std) [HU]', label='REDCNN')
    ax1.set_ylabel('CT Noise (ROI std) [HU]')
    f.tight_layout()
    if output_fname:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        f.savefig(output_fname, dpi=600)


def plot_relative_denoising(fbp_summary_df, proc_summary_df, output_fname=None, fig=None, ax=None):
    relative_denoising_df = proc_summary_df.set_index('Patient Diameter [mm]') / fbp_summary_df.set_index('Patient Diameter [mm]')
    relative_denoising_df.pop('mean CT number [HU]')
    relative_denoising_df*=100
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(4,4))
    relative_denoising_df.plot(ax=ax, ylabel='Noise Level Relative to FBP [%]\n$\sigma_{REDCNN} / \sigma_{FBP} \\times 100$')
    ax.get_legend().remove()
    if output_fname:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(output_fname, dpi=600)
    return fig, ax


def plot_noise_reduction(csv_fname, output_fname=None, fig=None, ax=None, reference_diameter=200):
    noise_reduction_df = get_noise_reduction_df(csv_fname)

    # noise_reduction_df.loc[len(noise_reduction_df.index)] = [200, 45.5730] #add adult reference data
    adult_df = noise_reduction_df[noise_reduction_df.index==reference_diameter]
    ped_df = noise_reduction_df[noise_reduction_df.index!=reference_diameter]
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(4,4))
    ped_df.plot(ax=ax, ylabel='Relative Noise Reduction [%]\n$|\sigma_{REDCNN} - \sigma_{FBP}| / \sigma_{FBP}\\times 100$')
    adult_df.plot(ax=ax, marker='*', markersize=10, color='black')
    ax.annotate('Adult Reference\n(340 mm FOV)', xy=(200, 50), horizontalalignment='center', arrowprops=dict(arrowstyle='->'), 
                bbox=dict(boxstyle='round', fc='white'), color='black')
    fovs = np.round(ped_df.index*1.1).astype(int).to_list()

    twiny = ax.twiny()
    twiny.set_xticks(np.linspace(min(fovs), max(fovs), 5).astype(int))
    twiny.set_xlim(ax.get_xlim())
    twiny.set_xlabel("Recon FOV [mm]")
    ax.get_legend().remove()
    fig.tight_layout()
    if output_fname:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(output_fname, dpi=600)
    return fig, ax


def get_bias_df(csv_fname):
    fbp_summary_df, proc_summary_df = load_csv(csv_fname)
    bias_df = proc_summary_df.set_index('Patient Diameter [mm]') - fbp_summary_df.set_index('Patient Diameter [mm]')
    bias_df.pop('mean noise (ROI std) [HU]')
    return bias_df


def plot_CT_bias(csv_fname, output_fname=None, fig=None, ax=None):
    bias_df = get_bias_df(csv_fname)
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(4,4))
    bias_df.plot(ax=ax, ylabel='CT number bias [HU]\n$REDCNN - FBP$')

    ax.plot(200, 50, marker='*', markersize=10, color='black')
    fovs = np.round(bias_df.index*1.1).astype(int).to_list()

    twiny = ax.twiny()
    twiny.set_xticks(np.linspace(min(fovs), max(fovs), 5).astype(int))
    twiny.set_xlim(ax.get_xlim())
    twiny.set_xlabel("Recon FOV [mm]")
    ax.annotate('Adult Reference\n(340 mm FOV)', xy=(200, 40), horizontalalignment='center', arrowprops=dict(arrowstyle='->'), 
            bbox=dict(boxstyle='round', fc='white'), color='black')
    ax.get_legend().remove()
    fig.tight_layout()
    if output_fname:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(output_fname, dpi=600)
    return fig, ax


def plot_CT_bias_v_noise_reduction(csv_fname, output_fname=None):
    bias_df = get_bias_df(csv_fname)
    noise_reduction_df = get_noise_reduction_df(csv_fname)
    f, ax = plt.subplots(figsize=(4,4))
    patient_diameter = bias_df.index
    im = ax.scatter(noise_reduction_df['mean noise (ROI std) [HU]'], bias_df['mean CT number [HU]'], c=patient_diameter)
    ax.set_xlabel('Relative Noise Reduction [%]\n$|\sigma_{REDCNN} - \sigma_{FBP}| / \sigma_{FBP}\\times 100$')
    ax.set_ylabel('CT Number Bias [HU]')
    cbar = plt.colorbar(im, label='Patient Diameter [mm]')
    f.tight_layout()

    if output_fname:
        f.savefig(output_fname, dpi=600)
        print(output_fname)


def get_noise_level_from_nps(delfreq, mag): return np.sqrt(sum(delfreq*mag))


def compare_NPS_noiselevel_and_ROI_measure(datadir, outdir):
    nps_csv_fname = f'{outdir}/diameter_1D_nps.csv'
    write_1D_nps_results_to_csv(datadir, nps_csv_fname, DOSELEVEL)

    print(nps_csv_fname)

    fbp_nps, proc_nps = load_csv(nps_csv_fname)

    delfreq = fbp_nps['spatial frequency [cyc/pix]'].diff()[1]
    diameters = [int(d.split('diameter')[1].split('mm')[0]) for d in fbp_nps.columns[1:]]
    fbp_noise_levels = [get_noise_level_from_nps(delfreq, fbp_nps[d]) for d in fbp_nps.columns[1:]]
    proc_noise_levels = [get_noise_level_from_nps(delfreq, proc_nps[d]) for d in proc_nps.columns[1:]]

    nps_noise_levels = pd.DataFrame({'Patient Diameter [mm]': diameters, 'FBP': fbp_noise_levels, 'REDCNN': proc_noise_levels}).set_index('Patient Diameter [mm]')

    fbp_summary_df, proc_summary_df = load_csv(f'{outdir}/diameter_summary.csv')
    fbp_summary_df.set_index('Patient Diameter [mm]', inplace=True)
    fbp_summary_df.pop('mean CT number [HU]')
    proc_summary_df.set_index('Patient Diameter [mm]', inplace=True)
    proc_summary_df.pop('mean CT number [HU]')
    roi_noise_levels = fbp_summary_df.join(proc_summary_df, rsuffix='_REDCNN-TV')
    roi_noise_levels.columns = [c + ' ROI' for c in nps_noise_levels.columns]
    nps_noise_levels.columns = [c + ' NPS' for c in nps_noise_levels.columns]
    noise_levels_df = pd.concat((roi_noise_levels, nps_noise_levels), axis=1)
    noise_levels_df.columns = sorted(noise_levels_df.columns)
    fname = f'{outdir}/nps_vs_roi_noise_levels.csv'
    noise_levels_df.to_csv(fname)
    print(fname)


def main(datadir=None, outdir=None):
    datadir = datadir or '/home/brandon.nelson/Data/temp/CCT189/monochromatic'
    datadir = Path(datadir)
    
    output_fname = f'{outdir}/plots/1D_nps.png'
    
    with plt.style.context('seaborn'):
   
        plot_1D_nps_all_diams(datadir, output_fname, sharex=True, sharey=True)
        print(output_fname)

        output_fname = f'{outdir}/diameter_summary.csv'
        csv_fname = write_results_to_csv(datadir, output_fname, DOSELEVEL)
        print(csv_fname)
        fbp_summary_df, proc_summary_df = load_csv(csv_fname)

        output_fname = f'{outdir}/plots/CT_number_noise_v_diameter.png'
        plot_CT_number_noise_v_diameter(fbp_summary_df, proc_summary_df, output_fname)
        print(output_fname)

        output_fname = f'{outdir}/plots/relative_noise_vs_diameter.png'
        _, rel_denoise_ax = plot_relative_denoising(fbp_summary_df, proc_summary_df)
        print(output_fname)

    output_fname = f'{outdir}/plots/noise_reduction_vs_diameter.png'
    _, noise_redux_ax = plot_noise_reduction(csv_fname, output_fname)
    print(output_fname)

    output_fname = f'{outdir}/plots/CT_number_bias.png'
    plot_CT_bias(csv_fname, output_fname)
    print(output_fname)


    output_fname = f'{outdir}/plots/bias_v_noise_reduction.png'
    plot_CT_bias_v_noise_reduction(csv_fname, output_fname)

    compare_NPS_noiselevel_and_ROI_measure(datadir, outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots 2D NPS images')
    parser.add_argument('--datadir', '-d', default=None,
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--output_dir','-o', required=False,
                        help="Directory to save image files")
    args = parser.parse_args()
    main(args.datadir, outdir=args.output_dir)
