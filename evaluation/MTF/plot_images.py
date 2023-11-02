import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd
import seaborn as sns

from utils.esf_plot import plot_patient_diameter_esf, load_esf_dataframe


def imread(fname, sz=None):
    sz = sz or int(pd.read_csv(Path(fname).parents[2] / 'geometry_info.csv').columns[1])
    return np.fromfile(open(fname), dtype=np.int16, count=sz*sz).reshape(sz, sz)


def image_comparison_with_diff(fbp_fname, proc_fname, outdir=None):

    diam = fbp_fname.parents[2].stem

    f, (ax0, ax1, ax2) = plt.subplots(1, 3, dpi=300,
                                    gridspec_kw=dict(hspace=0, wspace=0),
                                    sharex=True, sharey=True)
    orig = imread(fbp_fname)
    ax0.imshow(orig, cmap='gray')
    ax0.set_xlabel('FBP')
    ax0.xaxis.set_major_locator(plt.NullLocator())
    ax0.yaxis.set_major_locator(plt.NullLocator())

    redcnn = imread(proc_fname)
    ax1.imshow(redcnn, cmap='gray')
    ax1.set_xlabel('REDCNN')
    ax1.xaxis.set_major_locator(plt.NullLocator())
    ax1.yaxis.set_major_locator(plt.NullLocator())
    ax1.set_title(f'{diam}')

    im = ax2.imshow(redcnn - orig, cmap='gray')
    ax2.set_xlabel('REDCNN - FBP')
    ax2.xaxis.set_major_locator(plt.NullLocator())
    ax2.yaxis.set_major_locator(plt.NullLocator())
    cbar_ax = plt.gcf().add_axes([0.91, 0.325, 0.02, 0.34])
    plt.colorbar(im, cax=cbar_ax)

    if outdir is None: outdir = Path(__file__).parent / 'results' / 'images'
    outdir.mkdir(exist_ok=True, parents=True)
    fname = outdir / f'{diam}_image_comparison.png'
    f.savefig(fname, dpi=600)
    print(f'File saved: {fname}')


def get_lesion_info(fbp_fname):
    phantom_info = pd.read_csv(fbp_fname.parents[2] / 'phantom_info_pix_idx.csv')
    water_atten = phantom_info[' mu [60 keV] '][0]
    phantom_info['CT Number [HU]'] = 1000*(phantom_info[' mu [60 keV] '])/water_atten
    phantom_info.pop(' angle degree')
    return phantom_info.iloc[1:-1, :].sort_values(by='CT Number [HU]')


def get_lesion_coords(lesion_info, HU):
    all_lesions = lesion_info.round().astype(int)
    all_lesions.pop(' mu [60 keV] ')
    lesion = all_lesions[all_lesions['CT Number [HU]'] == HU]
    return (int(lesion['x center']), int(lesion[' y center'])), (int(lesion[' x radius']), int(lesion[' y radius']))


def imshow_with_profiles(fbp_fname, HUs, ax=None, colors=None):
    orig = imread(fbp_fname)

    phantom_info = get_lesion_info(fbp_fname)
    if ax is None:
        f, ax = plt.subplots()
    ax.imshow(orig[::-1, :], cmap='gray')
    colors = colors or ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w', 'orange']
    for hu, color in zip(HUs, colors):
        (xc, yc), (xr, yr) = get_lesion_coords(phantom_info, hu)
        ax.annotate('', (xc, yc), (xc + 1.75*xr, yc),
                        arrowprops={'arrowstyle': '-', 'linewidth': 2, 'color': color})
    return ax

def image_comparison_with_profile(fbp_fname, proc_fname, outdir=None, ylim=None):
    
    HUs = [15, 120, 340]
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w', 'orange']
    cons = [f' {c} HU' for c in HUs]
    fbp_df = load_esf_dataframe(fbp_fname.parents[1] / 'fbp_sharp_v001_esf.csv')[cons]
    proc_df = load_esf_dataframe(proc_fname.parents[1] / 'fbp_sharp_v001_esf.csv')[cons]

    diam = fbp_fname.parents[2].stem

    f, (ax0, ax1, ax2) = plt.subplots(1, 3, dpi=300, figsize=(14, 4))
    imshow_with_profiles(fbp_fname, HUs, ax=ax0, colors=colors)
    ax0.set_xlabel('FBP')
    ax0.xaxis.set_major_locator(plt.NullLocator())
    ax0.yaxis.set_major_locator(plt.NullLocator())

    redcnn = imread(proc_fname)
    ax1.imshow(redcnn[::-1, :], cmap='gray')
    ax1.set_xlabel('RedCNN')
    ax1.xaxis.set_major_locator(plt.NullLocator())
    ax1.yaxis.set_major_locator(plt.NullLocator())
    ax1.set_title(f'{diam}')

    plot_patient_diameter_esf(fbp_df, proc_df, ax=ax2, colors=colors)
    if ylim: ax2.set_ylim(ylim)
    if outdir:
        outdir = Path(outdir)
        outdir.mkdir(exist_ok=True, parents=True)
        fname = outdir / f'{diam}_image_comparison.png'
        f.savefig(fname, dpi=600)
        print(f'File saved: {fname}')
    else:
        f.show()


def main(datadir=None, outdir=None):
    datadir = datadir or '/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CTP404/monochromatic/'
    patient_dirs = sorted(list(Path(datadir).glob('diameter*')))

    sns.set_style("darkgrid")
    sns.set_context("talk")

    for patient in patient_dirs:
        proc_fname = sorted(list(patient.glob('I0_*_processed/fbp_sharp/*.raw')))[0]
        fbp_fname = sorted(list(patient.glob('I0_*0/fbp_sharp/*.raw')))[0]
        image_comparison_with_profile(fbp_fname, proc_fname, outdir, ylim=[-20, 350])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots ESF Curves')
    parser.add_argument('--datadir', '-d', default=None,
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--output_dir','-o', required=False,
                        help="Directory to save image files")
    args = parser.parse_args()
    main(args.datadir, outdir=args.output_dir)