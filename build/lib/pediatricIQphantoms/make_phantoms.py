from pathlib import Path
import argparse
import tomli
import numpy as np
import os

from oct2py import octave
import SimpleITK as sitk


def mirt_sim(phantom='CCT189', patient_diameter=200, reference_diameter=200, reference_fov=340, I0=3e5, nb=900, na=580, ds=1, sid=595, sdd=1085.6, offset_s=1.25, down=1, has_bowtie=False, add_noise=True, aec_on=True, nx=512, fov=340, fbp_kernel='hanning,2.05', nsims=1, relative_lesion_diameter=False):
    """
    Python wrapper for calling Michigan Image Reconstruction Toolbox (MIRT) Octave function 
    """
    if patient_diameter == reference_diameter:
        fov = reference_fov
    else:
        fov = 1.1*patient_diameter
    curdir = os.path.dirname(os.path.realpath(__file__))
    octave.cd(curdir)
    print(octave.pwd())
    return octave.ct_sim(phantom, patient_diameter, reference_diameter,    relative_lesion_diameter, I0, nb, na, ds, sdd, sid, offset_s, down, has_bowtie, add_noise, aec_on, nx, fov, fbp_kernel, nsims)


def run_batch_sim(image_directory: str, model=['CCT189'], diameter=[200], reference_diameter=200, framework='MIRT',
         nsims=1, nangles=580, aec_on=True, add_noise=True, full_dose=3e5,
         dose_level=[1.0], sid=595, sdd=1085.6, nb=880,
         ds=1, offset_s=1.25, fov=340, image_matrix_size=512, fbp_kernel='hanning,2.05', has_bowtie=True):
    """
    Return a list of random ingredients as strings.

    :param image_directory: Directory to save simulated outputs
    :type image_directory: str
    :param model: Optional, select phantom model to simulate current options include ['CCT189', 'CTP404']
    :type model: list[str]
    :param diameter: Optional, simulated phantom diameter in mm
    """

    image_directory = Path(os.path.abspath(image_directory))
    print(image_directory)
    phantoms = model

    dose_level = full_dose * np.array(dose_level)

    reference_fov = 340
    for phantom_idx, phantom in enumerate(phantoms):
        print(f'{phantom} Simulation series {phantom_idx}/{len(phantoms)}')
        for patient_diameter in diameter:
            for dose in dose_level:
                vol = mirt_sim(patient_diameter=patient_diameter, reference_diameter=reference_diameter, reference_fov=reference_fov, I0=dose, nb=nb, na=nangles, ds=ds, sid=sid, sdd=sdd, offset_s=offset_s, down=1, has_bowtie=has_bowtie, add_noise=add_noise, aec_on=aec_on, nx=image_matrix_size, fov=fov, fbp_kernel=fbp_kernel, nsims=nsims)

                savedir = image_directory / phantom / f'diameter{patient_diameter}mm' / f'I0_{int(dose):07d}' / 'disk'
                savedir.mkdir(exist_ok=True, parents=True)

                pixel_size = fov/image_matrix_size

                gt = sitk.GetImageFromArray(vol['ground_truth'])
                gt.SetSpacing((1, pixel_size, pixel_size))
                fname = image_directory / phantom / f'diameter{patient_diameter}mm' / f'{phantom}.mhd'
                sitk.WriteImage(gt, fname)
                print(f'saving: {fname}')

                img = sitk.GetImageFromArray(vol['recon'])
                img.SetSpacing((1, pixel_size, pixel_size))
                kernel_name = fbp_kernel.replace(',','')
                kernel_name = kernel_name.replace('.','')
                fname = savedir / f'{kernel_name}.mhd'
                sitk.WriteImage(img, fname)
                print(f'saving: {fname}')


def main():
    parser = argparse.ArgumentParser(description='Make Pediatric IQ Phantoms')
    parser.add_argument('config', nargs='?', default=None,
                        help="configuration toml file containing simulation parameters")
    args = parser.parse_args()

    if args.config:
        with open(args.config, mode="rb") as fp:
            config = tomli.load(fp)
    else:
        with open("configs/defaults.toml", mode="rb") as fp:
            config = tomli.load(fp)
    
    sim = dict()
    for c in config['simulation']:
        sim.update(c)
        run_batch_sim(**sim)

if __name__ == '__main__': main()