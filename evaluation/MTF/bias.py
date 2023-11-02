# %%

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from utils.esf_plot import plot_patient_diameter_esf, load_esf_dataframe
import seaborn as sns

basedir =  Path('/gpfs_projects/brandon.nelson/DLIR_Ped_Generalizability/geometric_phantom_studies/CTP404/monochromatic')

def get_bias_df(basedir, doselevel='I0_3000000'):
    for idx, patient_dir in enumerate(basedir.glob('diameter*mm')):
        fbp_df = load_esf_dataframe(patient_dir / doselevel / 'fbp_sharp_v001_esf.csv').set_index('distance [mm]')
        diam = fbp_df.pop('patient diameter [mm]').unique()[0]

        ct_number = [int(c.split(' HU')[0]) for c in fbp_df.columns]
        true_contrast = list(map(abs, ct_number))

        bias = (fbp_df.iloc[:len(fbp_df)//3].mean()  - true_contrast).to_list()
        ct_number.append(0)
        bias.append(fbp_df[' 15 HU'].iloc[2*len(fbp_df)//3:].mean())
        if idx > 0:
            bias_df = bias_df.join(pd.DataFrame({'CT Number [HU]': ct_number, diam : bias}).set_index('CT Number [HU]'))
        else:
            bias_df = pd.DataFrame({'CT Number [HU]': ct_number, diam : bias}).set_index('CT Number [HU]')
    return bias_df[sorted(bias_df.columns)].sort_index()

def get_error_df(basedir, doselevel='I0_3000000'):
    for idx, patient_dir in enumerate(basedir.glob('diameter*mm')):
        fbp_df = load_esf_dataframe(patient_dir / doselevel / 'fbp_sharp_v001_esf.csv').set_index('distance [mm]')
        diam = fbp_df.pop('patient diameter [mm]').unique()[0]

        ct_number = [int(c.split(' HU')[0]) for c in fbp_df.columns]
        true_contrast = list(map(abs, ct_number))

        error = abs((fbp_df[fbp_df.index < 10].mean()  - true_contrast))/true_contrast*100

        if idx > 0:
            error_df = error_df.join(pd.DataFrame({'CT Number [HU]': ct_number, diam : error}).set_index('CT Number [HU]'))
        else:
            error_df = pd.DataFrame({'CT Number [HU]': ct_number, diam : error}).set_index('CT Number [HU]')
    return error_df[sorted(error_df.columns)]
    # measured_contrast = fbp_df[fbp_df.index < 10].mean() - fbp_df[fbp_df.index > 25].mean()
    # error = (measured_contrast - true_contrast)/true_contrast*100

fbp_bias_df = get_bias_df(basedir, doselevel='I0_3000000')
proc_bias_df = get_bias_df(basedir, doselevel='I0_3000000_processed')

# %%
sns.heatmap(fbp_bias_df, annot=True)
# %%
sns.heatmap(proc_bias_df, annot=True)

# %%
sns.heatmap(abs(proc_bias_df), annot=True)
# %%
adult_ref = pd.DataFrame({'CT Number [HU]': [-35, 120, 340, 990], 150: [50, 58, 58, 65]}).set_index('CT Number [HU]')
sns.heatmap(abs(proc_bias_df.join(adult_ref)), annot=True)
# %%
import numpy as np
import matplotlib.patches as patches

def plot_bias_heatmap(bias_df, ax=None):
    if ax is None:
        f, ax = plt.subplots()
    sns.heatmap(bias_df, annot=True, ax=ax,
                cbar_kws=dict(label=f'Bias [HU]\n(REDCNN CT Number - True CT Number)'))
    ax.set_xlabel('Patient Diameter [mm]')
    twiny = ax.twiny()

    fovs = np.round(bias_df.columns*1.1).astype(int).to_list()
    fovs[bias_df.columns.to_list().index(150)] = 340 # From RZ, min FOV for adult scan protocol
    twiny.set_xticks(ax.get_xticks(), fovs)
    twiny.set_xlim(ax.get_xlim())
    twiny.set_xlabel("Recon FOV [mm]")
    nrows = len(bias_df)
    rect = patches.Rectangle((6, 0.05), 0.97, nrows-0.1, linewidth=3, edgecolor='tab:blue', facecolor='none')
    ax.annotate("Adult\nReference",
                xy=(6.75, nrows), xycoords='data',
                xytext=(0.725, 0.025), textcoords='figure fraction',
                color='tab:blue',
                arrowprops=dict(facecolor='tab:blue', shrink=0.05), weight='bold')
    ax.add_patch(rect)

# %%
output_dir = Path('../../results/HU Accuracy/')
output_dir.mkdir(exist_ok=True, parents=True)
f, ax = plt.subplots()
proc_bias_df = get_bias_df(basedir, doselevel='I0_3000000_processed')
plot_bias_heatmap(abs(proc_bias_df.join(adult_ref).sort_index(ascending=True)), ax=ax)
f.savefig(output_dir / 'bias_heatmap.png', dpi=600)
# %%
fovs = np.round(proc_bias_df.columns*1.1).astype(int).to_list()
fovs.append(340)
abs_bias = abs(proc_bias_df.join(adult_ref).sort_index(ascending=True)).mean()

f, ax = plt.subplots(figsize=(3,3))
pd.DataFrame({'FOV [mm]': fovs, '|bias| [HU]': abs_bias}).plot(ax=ax, x='FOV [mm]', y='|bias| [HU]', marker='*', kind='scatter')

f.savefig(output_dir / 'bias_v_fov.png', dpi=600)
# %%
