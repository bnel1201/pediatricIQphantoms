import argparse
from pathlib import Path
import os

import numpy as np
import pandas as pd


def imread(fname, sz=None):
    sz = sz or int(pd.read_csv(Path(fname).parents[2] / 'geometry_info.csv').columns[1])
    return np.fromfile(open(fname), dtype=np.int16, count=sz*sz).reshape(sz, sz)

def get_patient_diameter(simulations_dir, patient_name):
    return next((simulations_dir / patient_name).glob('*/diameter*mm')).stem

def get_dose_levels(diameter_dir):
    return [int(o.stem.split('_')[1]) for o in (diameter_dir).glob('I0_*0')]

def get_water_equivalent_diameter(ct_img, nx):
    """
    Water equivalent diameter is attenuation based cross-sectional diameter measure from AAPM TG204 Eq. 4b <https://www.aapm.org/pubs/reports/rpt_220.pdf>
    =====
    inputs
    ct_img: in HU
    nx: side length of image in units (e.g. 480 mm) 
    """
    return 2*np.sqrt(((ct_img - 1000).mean()/1000 + 1)*(nx**2)/np.pi) 

def load_patient(simulations_dir, patient_name):
    simulations_dir = Path(simulations_dir)
    diameter = get_patient_diameter(simulations_dir, patient_name)
    diameter_dir = simulations_dir / patient_name / f'monochromatic' / diameter
    dose_levels = sorted(get_dose_levels(diameter_dir))
    eff_diameter = int(diameter.split('diameter')[1].split('mm')[0])
    fbp_stack = []
    cnn_stack = []
    fbp_filenames = []
    cnn_filenames = []
    diameter_dir = simulations_dir / patient_name / f'monochromatic' / diameter
    for dose_level in dose_levels:
        fbp_dir = diameter_dir / f'I0_{dose_level:07.0f}/fbp_sharp/'
        cnn_dir = diameter_dir / f'I0_{dose_level:07.0f}_processed/fbp_sharp/'
        fbp_files = list(fbp_dir.glob('*.raw'))
        cnn_files = list(cnn_dir.glob('*.raw'))
        fbp_singledose_stack = np.stack([imread(o) for o in fbp_files])
        cnn_singledose_stack = np.stack([imread(o) for o in cnn_files])
        fbp_stack.append(fbp_singledose_stack)
        cnn_stack.append(cnn_singledose_stack)
        fbp_filenames.append(fbp_files)
        cnn_filenames.append(cnn_files)

    geom = pd.read_csv(diameter_dir / 'geometry_info.csv').set_index('nx').T
    pix_size = float(geom['dx'])
    matrix_size = int(geom['ny'])
    fov = pix_size * matrix_size
    true_im = imread(diameter_dir / 'true.raw', matrix_size)
    noiseless_im = imread(diameter_dir / 'noise_free.raw', matrix_size)
    water_equivalent_diameter = get_water_equivalent_diameter(true_im, fov)

    return {'fbp': np.stack(fbp_stack),
            'cnn' : np.stack(cnn_stack),
            'true' : true_im,
            'noiseless' : noiseless_im,
            'dose_levels' : dose_levels,
            'pix_size': pix_size,
            'effective_diameter':  eff_diameter,
            'water_equivalent_diameter': water_equivalent_diameter,
            'fbp_filenames': fbp_filenames,
            'cnn_filenames': cnn_filenames}


def rmse(a,b): return np.sqrt((np.mean((a.ravel() - b.ravel())**2)))

def mse_summary(a_stack, b_true): return np.array([rmse(a, b_true) for a in a_stack])

# consider turning this into a class...
def get_patient_name(patient): return ' '.join(patient.split('_')[:2])


def get_patient_code(patient_name):
    """
    this is the inverse of get_nrb_filenames
    """
    if patient_name.split(' ')[1][:2] == 'pt':
        code = patient_name.split(' ')[1][2:]
        return code
    
    code = 'Reference '
    if patient_name.split(' ')[1] == 'infant':
        code += 'newborn'
        return code
    age_int = int(patient_name.split(' ')[1][:-2])

    code += f'{age_int} yr old'
    if age_int < 15:
        return code
    
    gender = 'M' if patient_name.split(' ')[0] == 'male' else 'F'
    code += f' {gender}'
    return code

def get_patient_info(patient_info:pd.DataFrame, patient_code:str): return patient_info[patient_info['Code #'] == patient_code]

def get_patient_age(patient_info:pd.DataFrame, patient_code:str): return float(patient_info[patient_info['Code #'] == patient_code]['age (year)'])


def get_patient_gender(patient_info:pd.DataFrame, patient_code:str): return float(patient_info[patient_info['Code #'] == patient_code]['gender'])


def get_patient_height(patient_info:pd.DataFrame, patient_code:str): return float(patient_info[patient_info['Code #'] == patient_code]['height (cm)'])


def get_patient_weight_percentile(patient_info:pd.DataFrame, patient_code:str): return float(patient_info[patient_info['Code #'] == patient_code]['weight percentile'])


def get_patient_gender(patient_info:pd.DataFrame, patient_code:str): return patient_info[patient_info['Code #'] == patient_code]['gender'].values[0]


def get_patient_weight(patient_info:pd.DataFrame, patient_code:str): return float(patient_info[patient_info['Code #'] == patient_code]['weight (kg)'])


def get_patient_ethnicity(patient_info:pd.DataFrame, patient_code:str): return patient_info[patient_info['Code #'] == patient_code]['ethnicity'].values[0]


def get_patient_bmi(patient_info:pd.DataFrame, patient_code:str): return float(patient_info[patient_info['Code #'] == patient_code]['BMI'])


def main(simulations_dir, patient_info_csv_file, results_fname='anthro_mse_dataset.csv', length_units='cm'):
    simulations_dir = Path(simulations_dir)
    patients = os.listdir(simulations_dir)

    patient_names = [get_patient_name(patient) for patient in patients]
    patient_info = pd.read_csv(patient_info_csv_file)
    code_names = {get_patient_code(patient_name) : patient_name for patient_name in patient_names}

    if set(code_names.keys()) != set(patient_info['Code #']):
        raise RuntimeError(f'The patient codes in {patient_info_csv_file} do not agree with the simulations found in {simulations_dir}')

    fbp_mses = []
    cnn_mses = []
    eff_diameters = []
    weds = []
    fbp_filenames = []
    cnn_filenames = []
    for patient in patients:
        img_dict = load_patient(simulations_dir, patient)
        fbp_filenames.append(img_dict['fbp_filenames'])
        cnn_filenames.append(img_dict['cnn_filenames'])
        fbp_mse = [mse_summary(img_dict['fbp'][doseidx], img_dict['true']) for doseidx in range(len(img_dict['dose_levels']))]
        cnn_mse = [mse_summary(img_dict['cnn'][doseidx], img_dict['true']) for doseidx in range(len(img_dict['dose_levels']))]
        fbp_mses.append(fbp_mse)
        cnn_mses.append(cnn_mse)
        eff_diameters.append(img_dict['effective_diameter'])
        weds.append(img_dict['water_equivalent_diameter'])

    def get_patient_effective_diameter(patient_name, units='mm'):
        d = eff_diameters[patient_names.index(patient_name)]
        if units == 'mm':
            return d
        if units == 'cm':
            return d/10

    def get_patient_water_equivalent_diameter(patient_name, units='mm'):
        d = weds[patient_names.index(patient_name)]
        if units == 'mm':
            return d
        if units == 'cm':
            return d/10

    fbp_mses = np.stack(fbp_mses)
    cnn_mses = np.stack(cnn_mses)
    weds = np.stack(weds)
    fbp_filenames = np.stack(fbp_filenames)
    cnn_filenames = np.stack(cnn_filenames)

    patients = np.array(patients, dtype='S')
    eff_diameters = np.array(eff_diameters)
    doselevels = np.array(img_dict['dose_levels'])

    recon_type = ['fbp', 'cnn']
    nsims = fbp_mses.shape[-1]

    codes = []
    names = []
    doses = []
    mses = []
    recons = []
    age_list = []
    gender_list = []
    weight_list = []
    height_list = []
    bmi_list = []
    ethnicity_list = []
    weight_percentile_list = []
    effective_diameter_list = []
    wed_list = []
    sim_number = []
    file_names = []

    for recon in recon_type:
        for patient_idx, (code, name) in enumerate(code_names.items()):
            for dose_idx, dose in enumerate(doselevels):
                for sim_idx in range(nsims):
                    codes.append(code)
                    names.append(name)
                    doses.append(dose)
                    sim_number.append(sim_idx)
                    recons.append(recon)
                    age_list.append(get_patient_age(patient_info, code))
                    gender_list.append(get_patient_gender(patient_info, code))
                    height_list.append(get_patient_height(patient_info, code))
                    weight_list.append(get_patient_weight(patient_info, code))
                    bmi_list.append(get_patient_bmi(patient_info, code))
                    weight_percentile_list.append(get_patient_weight_percentile(patient_info, code))
                    effective_diameter_list.append(get_patient_effective_diameter(name, units=length_units))
                    ethnicity_list.append(get_patient_ethnicity(patient_info, code))
                    wed_list.append(get_patient_water_equivalent_diameter(name, units=length_units))
                    if recon == 'fbp':
                        mses.append(fbp_mses[patient_idx, dose_idx, sim_idx])
                        file_names.append(fbp_filenames[patient_idx, dose_idx, sim_idx])
                    else:
                        mses.append(cnn_mses[patient_idx, dose_idx, sim_idx])
                        file_names.append(cnn_filenames[patient_idx, dose_idx, sim_idx])

    xcat_df = pd.DataFrame({'Code #': codes,
                    'Name': names,
                    'age (year)': age_list,
                    'gender': gender_list,
                    'weight (kg)': weight_list,
                    'height (cm)': height_list,
                    'BMI': bmi_list,
                    'weight percentile': weight_percentile_list,
                    'ethnicity': ethnicity_list,
                    'effective diameter (cm)': effective_diameter_list,
                    'WED (cm)': wed_list,
                    'Dose (photons)' : doses,
                    'recon' : recons,
                    'simulation number': sim_number,
                    'RMSE' : mses,
                    'file': file_names})
    xcat_df.to_csv(results_fname, index=False)

    if results_fname:
        print(results_fname)
    else:
        print(xcat_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make Mean Squared Error Measurements on Anthropomorphic Phantoms')
    parser.add_argument('simulations_dir',
                        help="directory containing simulated CT data")
    parser.add_argument('patient_info_csv_file',
                        help="csv file containing virtual patient info in XCAT format")
    parser.add_argument('-o', '--output_filename',
                        help="csv file storing measured MSE values")
    args = parser.parse_args()
    main(args.simulations_dir, args.patient_info_csv_file, results_fname=args.output_filename)
