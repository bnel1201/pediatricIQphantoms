# %%

import argparse
import matplotlib.pyplot as plt
from pathlib import Path
from utils.img_io import (get_img_sz,
                          get_lesion_info,
                          get_image_offset,
                          get_lesion_coords,
                          imread,
                          imshow_disk_comparison)


def imshow_true_image(patient, output_dir=None):
    nx = get_img_sz(patient / 'geometry_info.csv')
    lesions = get_lesion_info(patient / 'phantom_info_pix_idx.csv')
    offset = get_image_offset(patient / 'image_info.csv')
    true_im = imread(patient / 'true_disk.raw', sz=nx) - offset

    f, ax = plt.subplots()
    ax.imshow(true_im[:, ::-1], cmap='gray', vmin=-1, vmax=15)
    r = lesions[' x radius'].max()*1.5
    for HU in lesions['CT Number [HU]']:
        (xc, yc), (xr, yr) = get_lesion_coords(lesions, round(HU))
        ax.annotate(f'{round(HU)} HU', (nx - xc, nx - yc-r),
                    xycoords='data', color='tab:blue', fontsize=14, horizontalalignment='center')
    ax.set_title('Noise-Free')
    if output_dir:
        output_fname = output_dir.parent / 'noise_free.png'
        output_fname.parent.mkdir(exist_ok=True, parents=True)
        f.savefig(output_fname, dpi=600)
        print(f'saved to: {output_fname}')
    else:
        f.show()


def main(h5file, datadir=None, n_avg=20, output_dir=None):
    datadir = datadir or '/home/brandon.nelson/Data/temp/CCT189/monochromatic'
    patient_dirs = sorted(list(Path(datadir).glob('diameter*')))

    output_dir = Path(output_dir) if output_dir else None

    imshow_true_image(patient_dirs[0], output_dir)

    for patient_dir in patient_dirs:
        imshow_disk_comparison(patient_dir, h5file, n_avg=n_avg, output_dir=output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots LCD images from CCT189')
    parser.add_argument('h5file', help="LCD_results.h5 file")
    parser.add_argument('--datadir', '-d', default=None,
                        help="directory containing different patient diameter CT simulations")
    parser.add_argument('--output_dir','-o', required=False,
                        help="Directory to save image files")
    parser.add_argument('--n_avg','-n', required=False,
                        help="Number of images to average when showing LCD images")
    args = parser.parse_args()
    n_avg = int(args.n_avg) if args.n_avg else None
    main(args.h5file, args.datadir, n_avg=n_avg, output_dir=args.output_dir)
