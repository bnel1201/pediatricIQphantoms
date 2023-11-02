import argparse
import re
from pathlib import Path
import os

import pandas as pd
import numpy as np

XCAT_dir = '/gpfs_projects/brandon.nelson/XCAT/XCAT_V2_LINUX/'
XCAT_MODELFILES_DIR='/gpfs_projects/brandon.nelson/XCAT/modelfiles'
XCAT = 'dxcat2_linux_64bit'


XCAT_MODELFILES_DIR = Path(XCAT_MODELFILES_DIR)

def get_diameter(df, code, units='mm'):
    diameter = float(df[df['Code #'] == code]['effective diameter (cm)'])
    if units == 'mm':
        diameter *= 10
    return diameter

def get_nrb_filenames(phantom_df, code):
    if phantom_df['Code #'].dtype != int: code = str(code)
    idx = phantom_df[phantom_df['Code #'] == code].index[0]
    patient_num = phantom_df['Code #'][idx]
    gender = phantom_df['gender'][idx]
    gender_str = 'female' if gender == 'F' else 'male'
    if str(patient_num).split(' ')[0] == 'Reference':
        age = int(phantom_df['age (year)'][idx])
        age_str = 'infant' if age < 1 else f'{age}yr'
        patient = f'{gender_str}_{age_str}_ref'
    else:
        patient = f'{gender_str}_pt{patient_num}'
    patient_nrb_file = XCAT_MODELFILES_DIR / f'{patient}.nrb'
    patient_heart_nrb_file =  XCAT_MODELFILES_DIR / f'{patient}_heart.nrb'
    return patient_nrb_file, patient_heart_nrb_file, patient

def get_phantom_bin_filename(phantoms_dir, patient): return phantoms_dir / f'{patient}_atn_1.bin'

def get_phantom_log_filename(phantoms_dir, patient): return phantoms_dir / f'{patient}_log'

def imread(fname, sz=1024, dtype=np.float32): return np.fromfile(open(fname), dtype=dtype, count=sz*sz).reshape(sz, sz)

def effective_diameter(ground_truth, pix_sz_mm): return 2*np.sqrt((ground_truth>0).sum()*pix_sz_mm**2/np.pi)

def get_patient_name(phantoms, code):
    _, _, patient = get_nrb_filenames(phantoms, code)
    return patient

def get_pixel_width(log_filename, units='mm'):
    """
    reads XCAT log file and returns pixel width in specified `units`
    """
    with open(log_filename, 'r') as f:
        text = f.read()
    m = re.search('(pixel width =  )(\d.\d+)', text)
    pixel_width = float(m.group(2))
    if units == 'mm':
        pixel_width *= 10
    return pixel_width

def get_array_size(log_filename):
    """
    reads XCAT log file and returns array size in pixels
    """
    with open(log_filename, 'r') as f:
        text = f.read()
    m = re.search('(array_size =\s+)(\d.\d+)', text)
    return int(m.group(2))

# def measure_effective_diameter(phantom_df, code, units='mm'):
#     patient = get_patient_name(phantom_df, code)
#     bin_file = get_phantom_bin_filename(phantoms_dir / 'full_fov', patient)
#     log_file = get_phantom_log_filename(phantoms_dir / 'full_fov', patient)
#     array_size = get_array_size(log_file)
#     pixel_width_mm = get_pixel_width(log_file, units=units)
#     ground_truth = imread(bin_file, sz=array_size)
#     return effective_diameter(ground_truth, pixel_width_mm)

def get_effective_diameter(phantom_df, code): return phantom_df[phantom_df['Code #']==code]['effective diameter (cm)'].to_numpy()[0]

def get_height(phantom_df, code): return phantom_df[phantom_df['Code #']==code]['height (cm)'].to_numpy()[0]

def get_age(phantom_df, code): return phantom_df[phantom_df['Code #']==code]['age (year)'].to_numpy()[0]

def make_phantom(phantoms_dir, phantom_df, code, fov=None, array_size = 1024, energy=60):
    """
    energy [keV]
    """
    # XCAT_dir = Path(XCAT_dir)
    GENERAL_PARAMS_FILE = os.path.abspath(Path(__file__).parent / 'anthro_phantom.par')
    phantoms_dir.mkdir(exist_ok=True, parents=True)
    
    patient_nrb_file, patient_heart_nrb_file, patient = get_nrb_filenames(phantom_df, code)
    height = get_height(phantom_df, code)
    # age = get_age(phantom_df, code)
    estimated_eff_diameter = get_diameter(phantom_df, code, units='cm')
    fov = fov or min(1.1*estimated_eff_diameter, 48) #in cm
    pixel_width_cm = fov / array_size


    liver_location = phantom_df[phantom_df['Code #']==code]['liver location (relative to height)'].to_numpy()[0]

    midslice = round(height / pixel_width_cm * liver_location)
    cmd = f'cd {XCAT_dir}\n./{XCAT} {GENERAL_PARAMS_FILE}\
             --organ_file {patient_nrb_file}\
             --heart_base {patient_heart_nrb_file}\
             --pixel_width {pixel_width_cm}\
             --slice_width {pixel_width_cm}\
             --array_size {array_size}\
             --energy {energy}\
             --startslice {midslice}\
             --endslice {midslice}\
             --arms_flag 0\
             {phantoms_dir}/{patient}'
    cmd
    os.system(cmd)
# %%

def main(phantoms_dir, xcat_patients_csv='selected_xcat_patients.csv'):

    phantoms_dir = Path(phantoms_dir)
    phantoms_dir.mkdir(exist_ok=True, parents=True)

    phantoms_df = pd.read_csv(xcat_patients_csv)

    codes = phantoms_df['Code #']
    for code in codes:
        patient_nrb_file, patient_heart_nrb_file, _ = get_nrb_filenames(phantoms_df, code)
        assert patient_nrb_file.exists()
        assert patient_heart_nrb_file.exists()

    assert len(phantoms_df) == len(list(XCAT_MODELFILES_DIR.glob('*_heart.nrb')))

    for code in codes:
        fov = 48
        print(f'making full fov: {fov} cm phantoms {code}')
        make_phantom(phantoms_dir / 'full_fov', phantoms_df, code, fov=fov)

    for code in codes:
        fov = int(1.3 * get_effective_diameter(phantoms_df, code))
        print(f'making adaptive fov: {fov} cm phantoms {code}')
        make_phantom(phantoms_dir / 'adaptive_fov', phantoms_df, code, fov=fov)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make Anthropomorphic Phantoms using XCAT')
    parser.add_argument('base_dir',
                        help="output directory to save XCAT phantom bin files")
    parser.add_argument('patient_info_csv_file',
                        help="csv file containing virtual patient info in XCAT format")
    args = parser.parse_args()
    main(phantoms_dir=Path(args.base_dir) / 'anthropomorphic' / 'phantoms', xcat_patients_csv=args.patient_info_csv_file)
