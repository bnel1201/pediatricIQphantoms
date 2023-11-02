# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
# %%
def load_results():
    ctp404_results = pd.read_csv('/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results/MTF/MTF_results.csv')
    ctp404_results.rename(columns={'phantom_diameter_mm': 'Diameter [mm]',
                                   'measured_HU': 'Measured HU',
                                   'expected_HU': 'Expected HU',
                                   'recon': 'Recon'}, inplace=True)
    ctp404_results = ctp404_results[ctp404_results['Diameter [mm]'] < 300]
    ctp404_results = ctp404_results[ctp404_results['Diameter [mm]'] != 150]
    ctp404_results = ctp404_results[ctp404_results['Expected HU'].abs() < 900]
    ctp404_results['Contrast'] = ctp404_results['Expected HU'].abs().astype('category') 
    ctp404_results.replace({'dl_REDCNN': 'DLIR', 'fbp': 'FBP'}, inplace=True)
    return ctp404_results
ctp404_results = load_results()
# %%
# ctp404_results = ctp404_results[ctp404_results['MTF50'] > 0]
# %%
f, axs = plt.subplots(1,2, tight_layout=True, figsize=(8, 4), sharey=True)
sns.lineplot(ax=axs[0], x='Diameter [mm]', y='MTF50', hue='Contrast', style='Recon', data=ctp404_results, palette='crest')
sns.lineplot(ax=axs[1], x='Diameter [mm]', y='MTF25', hue='Contrast', style='Recon', data=ctp404_results, palette='crest')
# %%
delta_mtf = ctp404_results[ctp404_results['Recon'] == 'FBP'][['Diameter [mm]', 'Contrast', 'dose_level_pct', 'MTF50']]
delta_mtf['$\Delta$MTF50 [lp/cm]'] = ctp404_results[ctp404_results['Recon'] == 'DLIR']['MTF50'].to_numpy() - ctp404_results[ctp404_results['Recon'] == 'FBP']['MTF50'].to_numpy()
delta_mtf['$\Delta$MTF25 [lp/cm]'] = ctp404_results[ctp404_results['Recon'] == 'DLIR']['MTF25'].to_numpy() - ctp404_results[ctp404_results['Recon'] == 'FBP']['MTF25'].to_numpy()
delta_mtf['$\Delta$MTF10 [lp/cm]'] = ctp404_results[ctp404_results['Recon'] == 'DLIR']['MTF10'].to_numpy() - ctp404_results[ctp404_results['Recon'] == 'FBP']['MTF10'].to_numpy()
delta_mtf = delta_mtf[delta_mtf['MTF50'] > 0]
delta_mtf = delta_mtf[delta_mtf['dose_level_pct'] == 100]

f, axs = plt.subplots(1,2, tight_layout=True, figsize=(8, 3))
plot = sns.lineplot(ax=axs[0], x='Diameter [mm]', y='$\Delta$MTF50 [lp/cm]', hue='Contrast', data=delta_mtf, palette='crest')
plot.get_legend().remove()
plot = sns.lineplot(ax=axs[1], x='Diameter [mm]', y='$\Delta$MTF10 [lp/cm]', hue='Contrast', data=delta_mtf, palette='crest')
handles, labels = plot.get_legend_handles_labels()
plot.get_legend().remove()
# plot = sns.lineplot(ax=axs[2], x='Diameter [mm]', y='$\Delta$MTF10', hue='Contrast', data=delta_mtf, palette='crest')
# plot.get_legend().remove()
f.legend(handles, labels, ncol=3, loc='upper center', 
                bbox_to_anchor=(0.5, 1.2), frameon=False, title='Contrast [HU]')
[ax.set_ylim([-0.35, 0.12]) for ax in axs]
f.savefig('mtf_v_diameter.png', dpi=600, bbox_inches='tight')
# %%

f, ax = plt.subplots(figsize=(4, 3))
plot = sns.lineplot(ax=ax,x='Diameter [mm]', y='Measured HU', style='Recon', hue='Expected HU', data=ctp404_results[ctp404_results['Expected HU']<340], palette='crest')
handles, labels = plot.get_legend_handles_labels()
plot.get_legend().remove()
f.legend(handles, labels, ncol=3, loc='upper center', 
                bbox_to_anchor=(0.5, 1.2), frameon=False)
f.tight_layout()
f.savefig('HU_v_diameter.png', dpi=600, bbox_inches='tight')
# %%
ctp404_results['HU error'] = ctp404_results['Measured HU'] - ctp404_results['Expected HU']
# %%
plot = sns.lineplot(x='fov_size_mm', y='HU error', hue='Expected HU', style='Recon', data=ctp404_results)
handles, labels = plot.get_legend_handles_labels()
plot.get_legend().remove()
f = plt.gcf()
f.legend(handles, labels, ncol=3, loc='upper center', 
                bbox_to_anchor=(0.5, 1.2), frameon=False, title='Contrast [HU]')
f.tight_layout()
# %%
HU_errors = ctp404_results[ctp404_results['Recon'] != 'FBP']['Measured HU'].to_numpy() - ctp404_results[ctp404_results['Recon'] == 'FBP']['Measured HU'].to_numpy()
HU_error_df = ctp404_results[ctp404_results['Recon'] != 'FBP'][['Diameter [mm]', 'fov_size_mm', 'Expected HU']].copy()
HU_error_df['HU error'] = HU_errors
HU_error_df
# %%
f, ax = plt.subplots(figsize=(4, 3))
plot = sns.lineplot(ax=ax, x='Diameter [mm]', y='HU error', hue='Expected HU', data=HU_error_df, palette='crest', errorbar='sd', err_style='bars', err_kws={'capsize': 4})
handles, labels = plot.get_legend_handles_labels()
ax.set_ylabel('HU Error\nDLIR - FBP')
plot.get_legend().remove()
f.legend(handles, labels, ncol=3, loc='upper center', 
                bbox_to_anchor=(0.5, 1.2), frameon=False, title='Contrast [HU]')
f.tight_layout()
f.savefig('hu_accuracy.png', dpi=600, bbox_inches='tight')
# %%
ctp404_results = load_results()
ctp404_results['dose_level_pct'] = (ctp404_results['dose_photons'] / 300000 * 100).astype(int)
ctp404_results = ctp404_results[ctp404_results['dose_level_pct'] < 1000]

HU_errors = ctp404_results[ctp404_results['Recon'] != 'FBP']['Measured HU'].to_numpy() - ctp404_results[ctp404_results['Recon'] == 'FBP']['Measured HU'].to_numpy()
HU_error_df = ctp404_results[ctp404_results['Recon'] != 'FBP'][['Diameter [mm]', 'fov_size_mm', 'Expected HU', 'dose_level_pct']].copy()
HU_error_df['HU error'] = HU_errors
HU_error_df
# %%
grouped = HU_error_df.groupby(['dose_level_pct', 'Expected HU', 'Diameter [mm]'])
mean_errors = grouped.mean()
std_errors = grouped.std()
mean_errors
# %%

dose = 100
f, ax = plt.subplots()
for hu in HU_error_df['Expected HU'].unique():
    x = mean_errors['HU error'][dose, hu].index
    y = mean_errors['HU error'][dose, hu].values
    y_err = std_errors['HU error'][dose, hu].values
    ax.errorbar(x, y, yerr=y_err, marker='o')
# %%
