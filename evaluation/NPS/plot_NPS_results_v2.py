# %% [markdown]
# needs to include noise reduction v diameter but with error bars
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# %%
nps_results = pd.read_csv('/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results/NPS/NPS_results.csv')
nps_results.rename(columns={'fov_size_mm': 'FOV [mm]', 'phantom_diameter_mm': 'Phantom Diameter [mm]'}, inplace=True)

# nps_results = nps_results[nps_results['phantom_diameter_mm'] != 200]
# adult_ref_results = 
# %%
fbp_std_noise = nps_results[nps_results['recon'] == 'fbp']['sample_std'].to_numpy()
cnn_std_noise = nps_results[nps_results['recon'] == 'dl_REDCNN']['sample_std'].to_numpy()

noise_reduction = nps_results[nps_results['recon'] == 'fbp'][['Phantom Diameter [mm]', 'FOV [mm]', 'dose_level_pct']].copy()
noise_reduction['noise reduction %'] = ((fbp_std_noise - cnn_std_noise)) / fbp_std_noise * 100
noise_reduction.head()
# %%
grouped = noise_reduction.groupby(['dose_level_pct', 'FOV [mm]'])

mean_noise_reduction = grouped.mean()
mean_noise_reduction

std_noise_reduction = grouped.std()

diameters = nps_results.sort_values(by='FOV [mm]')['Phantom Diameter [mm]'].unique()
fovs = nps_results['FOV [mm]'].unique()

dose_levels = [100, 25, 10]
ndoses = len(dose_levels)
f, ax = plt.subplots(1, 1, figsize=(3.5, 3), dpi=150)

for dose in dose_levels:
    mean_noise_reduction['noise reduction %'][dose].plot(ax=ax, yerr = std_noise_reduction['noise reduction %'][dose], label=f'{dose}% dose', capsize=3)
ax.set_ylabel('Noise Reduction [%]\n$(\sigma_{FBP} - \sigma_{DLIR}) / \sigma_{FBP}\\times 100$')
ax.legend()
ax.annotate('Adult Protocol\n200 mm phantom', xy=(340, 65), xycoords='data', xytext=(280, 10), textcoords='data', ha='center', arrowprops=dict(facecolor='black', shrink=0.05))

twiny = ax.twiny()
twiny.set_xticks(ax.get_xticks()/1.1, diameters)
twiny.set_xlim(ax.get_xlim())
twiny.set_xlabel("Phantom Diameter [mm]")

f.tight_layout()
f.savefig('noise_reduction_v_fov.png', dpi=600)
# %%

# %% [markdown]
# for Rongping: -	Update Noise reduction curve to only use 25% dose curve, x axis = diameter (have adult ref to the right) and send to Rongpin

grouped = noise_reduction.groupby(['dose_level_pct', 'Phantom Diameter [mm]'])
mean_noise_reduction = grouped.mean()
std_noise_reduction = grouped.std()

diameters = nps_results.sort_values(by='FOV [mm]')['Phantom Diameter [mm]'].unique()
fovs = nps_results['FOV [mm]'].unique()

dose_levels = [25]
ndoses = len(dose_levels)
f, ax = plt.subplots(1, 1, figsize=(3.5, 3), dpi=150)

for dose in dose_levels:
    ped_mean = mean_noise_reduction['noise reduction %'][dose]
    ped_std = std_noise_reduction['noise reduction %'][dose]
    adult_std = ped_std[ped_mean.index == 200]
    ped_std = ped_std[ped_mean.index != 200]
    adult_mean = ped_mean[ped_mean.index == 200]
    adult_mean.index = [310]
    ped_mean = ped_mean[ped_mean.index != 200]
    
    ped_mean.plot(ax=ax, yerr = ped_std, label=f'{dose}% dose', capsize=3)
    adult_mean.plot(ax=ax, yerr=adult_std, marker='*', color='black', label="", capsize=3)

twiny = ax.twiny()
twiny.set_xticks(ax.get_xticks()*1.1)
twiny.set_xlim(110, 355)
twiny.set_xlabel("Recon FOV [mm]")

ax.set_ylabel('Noise Reduction [%]\n$(\sigma_{FBP} - \sigma_{DLIR}) / \sigma_{FBP}\\times 100$')
ax.legend()
ax.annotate('Adult Protocol\n340 mm FOV', xy=(310, 70), xycoords='data', xytext=(265, 30), textcoords='data', ha='center', arrowprops=dict(facecolor='black', shrink=0.05))

f.tight_layout()
f.savefig('noise_reduction_v_diameter.png', dpi=600)
# %% [markdown]
# for AAPM
# https://www.aapm.org/pubs/reports/rpt_204.pdf
def age_to_eff_diameter(age):
    x = age
    a = 18.788598
    b = 0.19486455
    c = -1.060056
    d = -7.6244784
    y = a + b*x**1.5 + c *x**0.5 + d*np.exp(-x)
    eff_diam = y
    return eff_diam
# diam_to_age_dict = {age_to_eff_diameter(a).astype(int): a for a in range(0, 19)}



from matplotlib.patches import Circle
import matplotlib.patches as patches

grouped = noise_reduction.groupby(['dose_level_pct', 'Phantom Diameter [mm]'])
mean_noise_reduction = grouped.mean()
std_noise_reduction = grouped.std()

diameters = nps_results.sort_values(by='FOV [mm]')['Phantom Diameter [mm]'].unique()
fovs = nps_results['FOV [mm]'].unique()

dose_levels = [25]
ndoses = len(dose_levels)
f, ax = plt.subplots(1, 1, figsize=(3.5, 3), dpi=150)

for c, dose in zip(['#1f77b4', '#ff7f0e'], dose_levels):
    ped_mean = mean_noise_reduction['noise reduction %'][dose]
    ped_std = std_noise_reduction['noise reduction %'][dose]
    adult_std = ped_std[ped_mean.index == 200]
    ped_std = ped_std[ped_mean.index != 200]
    adult_mean = ped_mean[ped_mean.index == 200]
    adult_mean.index = [310]
    ped_mean = ped_mean[ped_mean.index != 200]
    
    ped_mean.plot(ax=ax, yerr = ped_std, label=f'{dose}% dose', capsize=3)
    adult_mean.plot(ax=ax, yerr=adult_std, marker='*', color='black', label="", capsize=3)

c = (310,71)
circ1 = patches.Ellipse(c,width=13, height=15,lw=2.,ec='k',fill=False)
# ax.add_artist(circ1)
circ1.set_clip_box(ax.bbox)


twiny = ax.twiny()
twiny.set_xticks(ax.get_xticks()*1.1)
twiny.set_xlim(110, 355)
twiny.set_xlabel("Recon FOV [mm]")

ax.set_ylabel('Noise Reduction [%]\n$(\sigma_{FBP} - \sigma_{DLIR}) / \sigma_{FBP}\\times 100$')
ax.legend()
ax.annotate('Adult Protocol\n340 mm FOV', xy=(310, 73), xycoords='data', xytext=(265, 35), textcoords='data', ha='center', arrowprops=dict(facecolor='black', shrink=0.05), fontsize=8)
ax.annotate('Age groups with\ncorresponding mean\nabdomen diameter', xy=(165, 8), xytext=(105, 30), arrowprops=dict(facecolor='black', shrink=0.2), fontsize=8)

ages = [1, 5, 10, 15, 18]
for a in ages:
    eff_diam = age_to_eff_diameter(a)*10
    ax.annotate(f'{a}yrs', xy=(eff_diam, 20), xycoords='data', xytext=(eff_diam, 0.5), ha='center', textcoords='data')

f.tight_layout()
f.savefig('noise_reduction_v_diameter.png', dpi=600)

# %% [markdown]
# now let's look at the peak noise frequency shift
nps_results = pd.read_csv('/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results/NPS/NPS_results.csv')
nps_results.rename(columns={'fov_size_mm': 'FOV [mm]', 'phantom_diameter_mm': 'Phantom Diameter [mm]'}, inplace=True)

recons = nps_results['recon'].unique()

nps_results = nps_results[nps_results['Phantom Diameter [mm]'] != 200]

grouped = nps_results.groupby(['recon', 'dose_level_pct','Phantom Diameter [mm]'])

nps_peak = grouped.mean()['nps_mean']
# %%

dose = 10
plt.plot(nps_peak['dl_REDCNN', dose] - nps_peak['fbp', dose])
plt.xlabel('Phantom Diameter')
plt.ylabel('$\Delta \overline{NPS}$\n$\overline{NPS}_{DLIR} - \overline{NPS}_{FBP}$')
# %%

# %%
