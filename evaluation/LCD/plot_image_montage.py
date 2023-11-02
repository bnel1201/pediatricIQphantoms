import argparse
from pathlib import Path
from telnetlib import DO

import matplotlib.pyplot as plt

from utils.img_io import imshow_disk_comparison


def main(h5file, datadir=None, output_fname=None, diams=[112, 292], n_avg=20):
    datadir = datadir or '/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CCT189/monochromatic'
    datadir = Path(datadir)
    diams = diams or [112, 292]
    f, axs = plt.subplots(len(diams), 2, gridspec_kw=dict(wspace=0, hspace=0), figsize=(4, 2*len(diams)))
    for idx, d in enumerate(diams):
        patient = datadir / f'diameter{d}mm'
        imshow_disk_comparison(patient, h5file, n_avg=n_avg, f=f, axs=axs[idx, :])
    [ax.set_xlabel('') for ax in axs[:-1, :][0]]
    if output_fname:
        Path(output_fname).parent.mkdir(exist_ok=True, parents=True)
        f.savefig(output_fname, dpi=600)
        print(f'saved to: {output_fname}')
    else:
        f.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots LCD images as a montage')
    parser.add_argument('h5file', help="LCD_results.h5 file")
    parser.add_argument('--datadir', '-d', default=None,
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--output_fname','-o', required=False,
                        help="Directory to save image files")
    parser.add_argument('--n_avg','-n', required=False,
                        help="Number of images to average when showing LCD images")
    parser.add_argument('--diameters', '-D', nargs='+',
                        help="Patient diameters to include [list of integers: 112 131 151 185 216 292], default is 112 292")
    args = parser.parse_args()
    diams = list(map(int, args.diameters[0].split(' '))) if args.diameters else None
    n_avg = int(args.n_avg) if args.n_avg else None
    main(args.h5file, datadir=args.datadir, n_avg=n_avg, diams=diams, output_fname=args.output_fname)
