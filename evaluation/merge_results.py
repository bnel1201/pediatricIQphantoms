# %%
import pandas as pd
import matplotlib.pyplot as plt


anthro_mse_df = pd.read_csv("/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/test/results/anthropomorphic/anthro_mse_dataset.csv")
nps_df = pd.read_csv("/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/test/results/NPS/diameter_1D_nps.csv")

# %% first join mtf50 and 10

def merge_mtf_csv_files(mtf_cutoff_csv1, mtf_cutoff_csv2):

    mtf_df_1 = pd.read_csv(mtf_cutoff_csv1)
    mtf_df_2 = pd.read_csv(mtf_cutoff_csv2)

    mtf_df = pd.concat([mtf_df_1, mtf_df_2], axis=0).reset_index(drop=True)
    mtf_df.replace('FBP Baseline', 'fbp', inplace=True)
    mtf_df.replace('REDCNN', 'cnn', inplace=True)
    mtf_df

    patient_size_dict = {c : int(c.split('mm')[0]) for c in mtf_df.columns if c[-2:] == 'mm'}
    contrasts = mtf_df['Contrast [HU]'].unique()
    recon_types = mtf_df['Series'].unique()
    mtf_cutoffs = mtf_df['%MTF cutoff'].unique()

    recon_types_list = []
    diameters_list = []
    contrasts_list = []
    mtf_cutoffs_list = []
    cutoff_frequency_list = []
    for recon in recon_types:
        for col_name, diameter in patient_size_dict.items():
            for cutoff in mtf_cutoffs:
                for con in contrasts:
                    recon_types_list.append(recon)
                    diameters_list.append(diameter)
                    contrasts_list.append(con)
                    mtf_cutoffs_list.append(cutoff)
                    cutoff_frequency_list.append(float(mtf_df[(mtf_df['Series'] == recon) & (mtf_df['Contrast [HU]'] == con) & (mtf_df['%MTF cutoff'] == cutoff)][col_name]))
    return pd.DataFrame({'Phantom' : 'CTP404',
                         'Contrast (HU)': contrasts_list,
                         'patient diameter (mm)' : diameters_list,
                         'recon' : recon_types_list,
                         'MTF Cutoff Value (%)' : mtf_cutoffs_list,
                         'MTF Cutoff Frequency (1/mm)' : cutoff_frequency_list})

# mtf50_csv = "/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/test/results/MTF/mtf50.csv"
# mtf10_csv = "/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/test/results/MTF/mtf10.csv"

mtf50_csv = "/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results_lower_doses/MTF/mtf50.csv"
mtf10_csv = "/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results_lower_doses/MTF/mtf10.csv"
new_mtf_df = merge_mtf_csv_files(mtf50_csv, mtf10_csv)
new_mtf_df.to_csv('mtf_dataset.csv', index=False)
new_mtf_df
# %%
rel_sharpness = new_mtf_df[new_mtf_df['recon']=='cnn']['MTF Cutoff Frequency (1/mm)'].to_numpy() / new_mtf_df[new_mtf_df['recon']=='fbp']['MTF Cutoff Frequency (1/mm)'].to_numpy()

rel_sharpness_df = new_mtf_df[new_mtf_df['recon']=='fbp']
rel_sharpness_df.pop('recon')
rel_sharpness_df['Relative Sharpness'] = rel_sharpness
rel_sharpness_df
# %%
f, ax = plt.subplots()
rel_sharpness_df[rel_sharpness_df['MTF Cutoff Value (%)'] == 50].plot.scatter(ax=ax, x='patient diameter (mm)', y='Relative Sharpness', c='Contrast (HU)', cmap='jet')
ax.set_ylim([0.7, 1.05])
# %% Now NPS
nps_df = pd.read_csv("/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results_lower_doses/NPS/diameter_1D_nps.csv")

nps_df
nps_df.replace('FBP', 'fbp', inplace=True)
nps_df.replace('REDCNN', 'cnn', inplace=True)
patient_size_dict = {c : int(c.split('diameter')[1].split('mm')[0]) for c in nps_df.columns if c[-2:] == 'mm'}
recon_types = nps_df['Series'].unique()


recon_types_list = []
diameters_list = []
nps_peak_frequency_list = []
for recon in recon_types:
    for col_name, diameter in patient_size_dict.items():
        recon_types_list.append(recon)
        diameters_list.append(diameter)
        temp_df = nps_df[nps_df['Series'] == recon]
        nps_peak_frequency_list.append(float(temp_df[temp_df[col_name] == temp_df[col_name].max()]['spatial frequency [cyc/pix]']))
new_nps_df = pd.DataFrame({
    'Phantom': 'CCT189',
    'patient diameter (mm)': diameters_list,
    'recon' : recon_types_list,
    'NPS Peak (cyc/pix)': nps_peak_frequency_list
})
new_nps_df.to_csv('nps_dataset.csv', index=False)
new_nps_df
# %% plot nps shift

nps_peak_shift = new_nps_df[new_nps_df['recon'] == 'cnn']['NPS Peak (cyc/pix)'].to_numpy() - new_nps_df[new_nps_df['recon'] == 'fbp']['NPS Peak (cyc/pix)'].to_numpy()
nps_peak_shift_df = new_nps_df[new_nps_df['recon'] == 'cnn'].reset_index(drop=True)

nps_peak_shift_df.pop('recon')
nps_peak_shift_df.pop('NPS Peak (cyc/pix)')

nps_peak_shift_df['NPS Peak Shift (cyc/pix)'] = nps_peak_shift
nps_peak_shift_df
# %%
nps_peak_shift_df.plot(x='patient diameter (mm)', y='NPS Peak Shift (cyc/pix)')
# %% merge temp result

merged_df = pd.concat([new_mtf_df, new_nps_df])
merged_df.to_csv('merged_dataset.csv', index=False)
merged_df
# %%
