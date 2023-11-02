import argparse
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt

from utils.esf_plot import plot_patient_diameter_esf, load_esf_dataframe


def main(datadir=None, output_fname=None):
    datadir = datadir or '/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CTP404/monochromatic/'
    patient_dirs = sorted(list(Path(datadir).glob('diameter*')))

    sns.set_style("darkgrid")
    # sns.set_context("talk")
    f, axs = plt.subplots(2, 3, figsize=(9,6), sharex=True, sharey=True,
                        gridspec_kw=dict(hspace=0.1, wspace=0.1))
    for idx, (patient_dir, ax) in enumerate(zip(patient_dirs, axs.flatten())):
        cons = [f' {c} HU' for c in [-35]]
        fbp_df = load_esf_dataframe(patient_dir / 'I0_3000000' / 'fbp_sharp_v001_esf.csv')
        diameter = fbp_df['patient diameter [mm]'].unique()[0]
        fbp_df = fbp_df[cons]
        proc_df = load_esf_dataframe(patient_dir / 'I0_3000000_processed' / 'fbp_sharp_v001_esf.csv')[cons]
        legend = True if idx==0 else False
        plot_patient_diameter_esf(fbp_df, proc_df, ax=ax, title=f'{diameter}mm', legend=legend)
    if output_fname is None:
        plt.show()
    else:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        f.savefig(output_fname, dpi=600)
        print(f'File saved: {output_fname}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots ESF Curves')
    parser.add_argument('--datadir', '-d', default=None,
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--output_fname','-o', required=False,
                        help="filename for the saved plot")
    args = parser.parse_args()
    main(args.datadir, output_fname=args.output_fname)
