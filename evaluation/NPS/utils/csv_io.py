import pandas as pd


def get_diameter(patient_dir): return int(patient_dir.stem.split('diameter')[1].split('mm')[0])


def get_image_offset(nps_dir): return int(pd.read_csv(nps_dir.parents[1] / 'image_info.csv').columns[1])


def get_stats_df(nps_dir): return pd.read_csv(nps_dir / 'roi_stats.csv')


def get_diameter_summary_df(diam_dirs, relative_series_dir):
    diameters = []
    mean_vals = []
    noise_vals = []
    for patient_dir in diam_dirs:
        nps_dir = patient_dir / relative_series_dir / 'NPS'
        stats_df = get_stats_df(nps_dir)
        offset = get_image_offset(nps_dir)
        noise_vals.append(stats_df[' std [HU]'].mean())
        mean_vals.append(stats_df[' mean [HU]'].mean() - offset)
        diameters.append(get_diameter(patient_dir))
    return pd.DataFrame({'Patient Diameter [mm]': diameters, 'mean CT number [HU]': mean_vals, 'mean noise (ROI std) [HU]': noise_vals})


def get_1D_NPS_for_all_diams(base_dir, relative_series_dir):
    diams = []
    mags = []
    diam_dirs = sorted(list(base_dir.glob('diameter*')))
    for patient_dir in diam_dirs:
        nps_df = pd.read_csv(patient_dir / relative_series_dir / 'NPS' / '1D_nps.csv')
        freq = nps_df['spatial frequency [cyc/pix]']
        diams.append(patient_dir.stem)
        mags.append(nps_df[' magnitude'])
    nps_df = pd.DataFrame({d: mag for d,mag in zip(diams, mags)})
    nps_df['spatial frequency [cyc/pix]'] = freq
    nps_df.set_index('spatial frequency [cyc/pix]', inplace=True)
    return nps_df


def write_results_to_csv(base_dir, output_fname, DOSELEVEL):
    diam_dirs = sorted(list(base_dir.glob('diameter*')))
    fbp_summary_df = get_diameter_summary_df(diam_dirs, DOSELEVEL)
    proc_summary_df = get_diameter_summary_df(diam_dirs, DOSELEVEL + '_processed')
    fbp_summary_df['Series'] = 'FBP'
    proc_summary_df['Series'] = 'REDCNN'
    pd.concat((fbp_summary_df, proc_summary_df), axis=0).to_csv(output_fname, index=None)
    return output_fname


def write_1D_nps_results_to_csv(base_dir, output_fname, DOSELEVEL):
    fbp_nps_df = get_1D_NPS_for_all_diams(base_dir, DOSELEVEL)
    proc_nps_df = get_1D_NPS_for_all_diams(base_dir, DOSELEVEL+'_processed')
    fbp_nps_df['Series'] = 'FBP'
    proc_nps_df['Series'] = 'REDCNN'
    pd.concat((fbp_nps_df, proc_nps_df), axis=0).to_csv(output_fname)


def load_csv(csv_fname):
    df = pd.read_csv(csv_fname)
    fbp_summary_df = df[df['Series'] == 'FBP']
    fbp_summary_df.pop('Series')
    proc_summary_df = df[df['Series'] != 'FBP']
    proc_summary_df.pop('Series')
    return fbp_summary_df, proc_summary_df


def get_noise_reduction_df(csv_fname):
    fbp_summary_df, proc_summary_df = load_csv(csv_fname)
    fbp_summary_df.set_index('Patient Diameter [mm]', inplace=True)
    proc_summary_df.set_index('Patient Diameter [mm]', inplace=True)
    noise_reduction_df = abs((proc_summary_df - fbp_summary_df)/fbp_summary_df*100)
    noise_reduction_df.pop('mean CT number [HU]')
    return noise_reduction_df
