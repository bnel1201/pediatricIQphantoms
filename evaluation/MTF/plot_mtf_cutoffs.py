import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from utils.mtf_cutoffs import merge_patient_diameters, abs_HU


def main(datadir=None, output_fname=None, processed=False):
    datadir = datadir or '/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/main/CTP404/monochromatic/'
    patient_dirs = sorted(list(Path(datadir).glob('diameter*')))
    sns.set_style("darkgrid")
    # sns.set_context("talk")

    ylim = [0, 13]
    f, (ax0, ax1) = plt.subplots(1, 2, figsize=(8, 4))
    mtf50 = merge_patient_diameters(patient_dirs, mtfval=50, processed=processed)
    mtf50*=10
    mtf50.plot(ax=ax0, kind='bar', ylabel='50% MTF [lp/cm]')
    ax0.set_ylim(ylim)
    mtf10 = merge_patient_diameters(patient_dirs, mtfval=10, processed=processed)
    mtf10*=10
    mtf10.plot(ax=ax1, kind='bar', ylabel='10% MTF [lp/cm]')
    ax1.set_ylim(ylim)
    ax1.get_legend().remove() 

    f.tight_layout()
    if output_fname is None:
        plt.show()
    else:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        f.savefig(output_fname, dpi=600)
        print(f'File saved: {output_fname}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots MTF Cutoffs')
    parser.add_argument('--datadir', '-d',
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--output_fname', '-o', required=False,
                        help="filename for the saved plot")
    parser.add_argument('--processed', action='store_true', default=False,
                        help='boolean to plot the processed results, defaults to false using the baseline')
    args = parser.parse_args()
    main(args.datadir, output_fname=args.output_fname, processed=args.processed)