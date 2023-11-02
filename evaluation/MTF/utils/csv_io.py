import pandas as pd
from pathlib import Path

import scipy

def write_cutoffs_to_csv(mtf_baseline, mtf_processed, cutoff_val, output_fname):
    mtf_baseline = mtf_baseline.copy()
    mtf_processed = mtf_processed.copy()
    mtf_baseline['Series'] = 'FBP Baseline'
    mtf_processed['Series'] = 'REDCNN'
    mtf_baseline['%MTF cutoff'] = cutoff_val
    mtf_processed['%MTF cutoff'] = cutoff_val
    pd.concat((mtf_baseline, mtf_processed), axis=0).to_csv(output_fname)
    print(f'File saved: {output_fname}')

def write_relative_sharpness_to_csv(mtf50_rel, mtf10_rel, output_fname):
    mtf50_rel = mtf50_rel.copy()
    mtf10_rel = mtf10_rel.copy()
    mtf50_rel['%MTF cutoff'] = 50
    mtf10_rel['%MTF cutoff'] = 10
    pd.concat((mtf50_rel, mtf10_rel), axis=0).to_csv(output_fname)
    print(f'File saved: {output_fname}')

def load_csv(csv_fname):
    df = pd.read_csv(csv_fname)
    mtf50_rel = df[df['%MTF cutoff'] == 50]
    mtf10_rel = df[df['%MTF cutoff'] == 10]
    return mtf50_rel, mtf10_rel


def append_adult_data_to_mtf_cutoff_data(mtf_results_dir, cutoff_val, reference_diameter=150):
    ped_data = pd.read_csv(Path(mtf_results_dir) / f'mtf{cutoff_val}.csv')
    ped_fbp = ped_data[ped_data['Series'] == 'FBP Baseline']
    ped_redcnn = ped_data[ped_data['Series'] == 'REDCNN']
    ped_redcnn.pop('Series')
    ped_redcnn.pop('%MTF cutoff')
    ped_fbp.pop('Series')
    ped_fbp.pop('%MTF cutoff')

    # adult_mtf_dir = Path('/gpfs_projects/prabhat.kc/lowdosect/transfers/transfers_4_spie/exps/quant_analysis/mtf/results/matfiles')
    # adult_redcnn = scipy.io.loadmat(adult_mtf_dir / 'no_norm/redcnn/sharp_augTrTaTdT.mat')
    # These Contrast values are from PKC's poster located here: <S:\DIDSR\Research\DLIR Project\ConferencePresentations\ct_2022>
    redcnn_data = ped_redcnn.sort_values(by='Contrast [HU]').set_index('Contrast [HU]')
    adult_redcnn = redcnn_data.pop(f'{reference_diameter}mm')
    redcnn_data = redcnn_data.join(adult_redcnn)
    redcnn_data.rename(columns={f'{reference_diameter}mm':f'{reference_diameter}mm (Adult Reference)'}, inplace=True)
    # redcnn_data = redcnn_data.join(pd.DataFrame({'Contrast [HU]': [35, 120, 340, 990], '150mm (Adult Reference)': adult_redcnn[f'mtf{cutoff_val}_all'][::-1].squeeze()}).set_index('Contrast [HU]'))

    # adult_fbp = scipy.io.loadmat(adult_mtf_dir / 'sharp_fbp.mat')
    fbp_data = ped_fbp.sort_values(by='Contrast [HU]').set_index('Contrast [HU]')
    adult_fbp = fbp_data.pop(f'{reference_diameter}mm')
    fbp_data = fbp_data.join(adult_fbp)
    fbp_data.rename(columns={f'{reference_diameter}mm':f'{reference_diameter}mm (Adult Reference)'}, inplace=True)
    # fbp_data = fbp_data.join(pd.DataFrame({'Contrast [HU]': [35, 120, 340, 990], '150mm (Adult Reference)': adult_fbp[f'mtf{cutoff_val}_all'][::-1].squeeze()}).set_index('Contrast [HU]'))
    return fbp_data, redcnn_data