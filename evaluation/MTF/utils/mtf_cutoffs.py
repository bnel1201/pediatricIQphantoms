import pandas as pd


def clean_column_names(df):
    HUs = [round(float(h.split(' HU')[0])) for h in df.columns[1:]]
    new_cols = [df.columns[0]] + [f' {h} HU' for h in HUs]
    return df.rename(columns={old:new for old,new in zip(df.columns, new_cols)})


def sort_HU_cols(df):
    HUs = sorted([int(h.split(' HU')[0]) for h in df.columns[1:]])
    cols = [df.columns[0]]
    cols += [f' {h} HU' for h in HUs]
    return df[cols]


def get_mtf_results(patient_dir, mtfval=10, processed=False):
    if processed:
        cutoffs_csv_fname = patient_dir / 'I0_3000000_processed' / f'results_MTF{mtfval}.csv'
    else:
        cutoffs_csv_fname = patient_dir / 'I0_3000000' / f'results_MTF{mtfval}.csv'
    
    df = pd.read_csv(cutoffs_csv_fname)
    diameter = patient_dir.stem.split('diameter')[1]
    df = clean_column_names(df)
    df = sort_HU_cols(df)
    HUs = [int(h.split(' HU')[0]) for h in df.columns[1:]]
    mtf = df.iloc[0,1:].to_numpy()
    return pd.DataFrame({'Contrast [HU]': HUs, f'{diameter}': mtf})


def merge_patient_diameters(patient_dirs, mtfval=10, processed=False):
    mtf = get_mtf_results(patient_dirs[0], mtfval, processed=processed)
    for idx in range(1, len(patient_dirs)):
        other_mtf = get_mtf_results(patient_dirs[idx], mtfval, processed=processed)
        mtf=mtf.merge(other_mtf, how='inner', on='Contrast [HU]')
        mtf = mtf.set_index('Contrast [HU]')
    return mtf


def abs_HU(mtf_df, ascending=False):
    mtf_df = mtf_df.reset_index()
    mtf_df['Contrast [HU]'] = abs(mtf_df['Contrast [HU]'])
    mtf_df.sort_values(by='Contrast [HU]', ascending=ascending, inplace=True)
    return mtf_df.set_index('Contrast [HU]')
