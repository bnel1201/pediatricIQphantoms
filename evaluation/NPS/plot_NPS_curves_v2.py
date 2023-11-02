# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
nps_curves = pd.read_csv('/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results/NPS/diameter_1D_nps.csv')
# %%
diameters = [int(d.split('diameter')[1].split('mm')[0]) for d in nps_curves.columns if d.startswith('diameter')]
diameters.remove(200)
diameters
# %%
freq = []
noise_power = []
Series = []
diameters_list = []
for s in ['FBP', 'REDCNN']:
    for d in diameters:
        freq.extend(nps_curves[nps_curves['Series'] == s]['spatial frequency [cyc/pix]'].to_numpy())
        noise_power.extend(nps_curves[nps_curves['Series'] == s][f'diameter{d}mm'].to_numpy())
        Series.extend(nps_curves[nps_curves['Series'] == s]['Series'])
        diameters_list.extend([d]*len(nps_curves[nps_curves['Series'] == s]['Series']))
nps_df = pd.DataFrame({'Spatial Frequency [cyc/pix]': freq,
                       'Noise Power': noise_power,
                       'Phantom Diameter [mm]': diameters_list,
                       'Reconstruction': Series})
nps_df['Reconstruction'] = nps_df['Reconstruction'].astype('category')
nps_df.replace('REDCNN', 'DLIR', inplace=True)
# %%
bool_filt = [d in [112, 151, 185, 216, 292] for d in nps_df['Phantom Diameter [mm]']]
f, ax = plt.subplots(figsize=(4.5, 3.5), tight_layout=True)
sns.lineplot(ax=ax, x='Spatial Frequency [cyc/pix]', y='Noise Power', hue='Phantom Diameter [mm]', style='Reconstruction', data=nps_df[bool_filt], palette='crest')
ax.set_ylabel('Noise Power [HU$^2$]')
f.savefig('nps_curves.png', dpi=600)
# %%
