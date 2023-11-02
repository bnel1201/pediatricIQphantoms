from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from measure_anthro_mse import load_patient


def imread(fname, sz=None):
    sz = sz or int(pd.read_csv(Path(fname).parents[2] / 'geometry_info.csv').columns[1])
    return np.fromfile(open(fname), dtype=np.int16, count=sz*sz).reshape(sz, sz)


def make_relative_mse_reduction_dataframe(raw_dataframe):
    fbp_df = raw_dataframe[raw_dataframe['recon'] == 'fbp']
    cnn_df = raw_dataframe[raw_dataframe['recon'] == 'cnn']
    mse_reduction = 100*abs(fbp_df['RMSE'].to_numpy() - cnn_df['RMSE'].to_numpy()) / fbp_df['RMSE'].to_numpy()
    rel_mse_df = fbp_df.copy()
    rel_mse_df.pop('recon')
    rel_mse_df['RMSE Reduction (%)'] = mse_reduction
    rel_mse_df['Dose (%)'] = 100*rel_mse_df['Dose (photons)']/rel_mse_df['Dose (photons)'].max()
    return rel_mse_df


def main(result_csv_filename='anthro_mse_dataset.csv', output_dir='anthro_results'):

    xcat_df = pd.read_csv(result_csv_filename)
    rel_mse_df = make_relative_mse_reduction_dataframe(xcat_df)

    plots_dir = Path(output_dir) / 'plots'
    plots_dir.mkdir(exist_ok=True, parents=True)

    rel_mse_df.plot.scatter(x='age (year)', y='RMSE Reduction (%)', c='Dose (%)')
    output_fname = plots_dir / 'rmse_reduction_v_age.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')

    rel_mse_df.plot.scatter(x='effective diameter (cm)', y='RMSE Reduction (%)', c='Dose (%)')
    output_fname = plots_dir / 'rmse_reduction_v_eff_diameter.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')

    rel_mse_df.plot.scatter(x='WED (cm)', y='RMSE Reduction (%)', c='Dose (%)')
    output_fname = plots_dir / 'rmse_reduction_v_wed.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')

    doselevels_pct = rel_mse_df['Dose (%)'].unique()/100

    def get_closest_doselevel_idx(desired_doselevel):
        dose_idx = np.argmin(np.abs(doselevels_pct - desired_doselevel))
        return dose_idx

    imgs_dir = Path(output_dir) / 'images'
    imgs_dir.mkdir(exist_ok=True, parents=True)

    codes = rel_mse_df['Code #'].unique()
    for code in codes:
        age_yrs = rel_mse_df[rel_mse_df['Code #'] == code]['age (year)'].unique()[0]
        weight_kg = rel_mse_df[rel_mse_df['Code #'] == code]['weight (kg)'].unique()[0]
        eff_diameter = rel_mse_df[rel_mse_df['Code #'] == code]['effective diameter (cm)'].unique()[0]
        wed = rel_mse_df[rel_mse_df['Code #'] == code]['WED (cm)'].unique()[0]
        desired_doselevels = [1, 0.5, 0.25]
        doseidxs = [get_closest_doselevel_idx(desired_doselevel) for desired_doselevel in desired_doselevels]

        basedir = Path(rel_mse_df[rel_mse_df['Code #'] == code]['file'].to_list()[0]).parents[5]
        patient = Path(rel_mse_df[rel_mse_df['Code #'] == code]['file'].to_list()[0]).parents[4].stem
        img_dict = load_patient(basedir, patient)
        base_images = np.concatenate([img_dict['true'], img_dict['noiseless']],axis=1)
        noisey_images = np.concatenate([
            np.concatenate([img_dict['fbp'][d, 0], img_dict['cnn'][d, 0]],axis=1) for d in doseidxs],axis=0)
        f, ax = plt.subplots(dpi=300)
        ww = 400
        wl = 0
        offset = 1000
        ax.imshow(np.concatenate([base_images,
                                noisey_images])-offset, cmap='gray', vmin=wl-ww/2, vmax=wl+ww/2)
        ax.tick_params(left = False, right = False , labelleft = False ,
                        labelbottom = False, bottom = False)
        nx = img_dict['true'].shape[0]
        ax.annotate('Ground Truth', (nx//2, nx//6),
                    xycoords='data',
                    color='white',
                    fontsize=8,
                    horizontalalignment='center')
        ax.annotate('Noiseless FBP', (nx + nx//2, nx//6),
                    xycoords='data',
                    color='white',
                    fontsize=8,
                    horizontalalignment='center')
        ax.annotate('Noiseless FBP', (nx + nx//2, nx//6),
                    xycoords='data',
                    color='white',
                    fontsize=8,
                    horizontalalignment='center')
        for idx, dl in enumerate(doselevels_pct[doseidxs]):
            ax.annotate(f'FBP {int(dl*100)}% dose', (nx//2, nx*(idx+1) + nx//6),
                    xycoords='data',
                    color='white',
                    fontsize=6,
                    horizontalalignment='center')
            ax.annotate(f'DLIR {int(dl*100)}% dose', (nx + nx//2, nx*(idx+1) + nx//6),
                        xycoords='data',
                        color='white',
                        fontsize=6,
                        horizontalalignment='center')
        ax.set_title(f"{code}\nAge: {age_yrs} yrs, Weight: {weight_kg} kg\nEff. Diameter {eff_diameter:2.1f} cm, WED: {wed:2.1f} cm", fontsize=6)
        output_fname = imgs_dir / f'{code}_montage.png'
        f.savefig(output_fname, dpi=600)
        print(f'Saving: {output_fname}')

    phantom_info_dir = Path(output_dir) / 'patient_population_summary'
    phantom_info_dir.mkdir(exist_ok=True, parents=True)
    xcat_df.plot.scatter(x='age (year)', y='weight (kg)')
    output_fname = phantom_info_dir / 'age_v_weight.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')

    xcat_df.plot.scatter(y='effective diameter (cm)', x='weight (kg)')
    output_fname = phantom_info_dir / 'weight_v_eff_diameteer.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')

    xcat_df.plot.scatter(y='WED (cm)', x='weight (kg)')
    output_fname = phantom_info_dir / 'weight_v_wed.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')

    xcat_df.plot.scatter(x='effective diameter (cm)', y = 'WED (cm)')
    output_fname = phantom_info_dir / 'eff_diameter_v_wed.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')

    xcat_df.plot.scatter(y='effective diameter (cm)', x='age (year)')
    output_fname = phantom_info_dir / 'eff_diameter_v_age_measured.png'
    plt.savefig(output_fname, dpi=600)
    print(f'Saving: {output_fname}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot Mean Squared Error Measurements on Anthropomorphic Phantoms')
    parser.add_argument('csv_file',
                        help="csv file containing MSE measurements from `measure_anthro_phantom.py`")
    parser.add_argument('-o', '--output_directory',
                        help="directory storing generated plots")
    args = parser.parse_args()
    main(result_csv_filename=args.csv_file, output_dir=args.output_directory)
