import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from matplotlib.lines import Line2D

def load_esf_dataframe(mtf_csv_fname):
    mtf_csv_fname = Path(mtf_csv_fname)
    df = pd.read_csv(mtf_csv_fname)
    index = 'distance [mm]'
    HUs = sorted([int(h.split(' HU')[0]) for h in df.columns[1:]])
    cols = [index]
    cols += [f' {h} HU' for h in HUs]
    df = df[cols]
    diameter = int(mtf_csv_fname.parents[1].stem.split('diameter')[1].split('mm')[0])
    df['patient diameter [mm]'] = diameter
    return df

def plot_patient_diameter_esf(fbp_df:pd.DataFrame, proc_df:pd.DataFrame, ax=None, title='', legend=True, colors=['b', 'g' ,'r']):
    if ax is None:
        f, ax = plt.subplots()

    fbp_linestyle='-'
    proc_linestyle='--'
    custom_lines = [Line2D([0], [0], color='black', linestyle=fbp_linestyle),
                    Line2D([0], [0], color='black', linestyle=proc_linestyle)]
    if ax is None:
        f, ax = plt.subplots(figsize=(4,4))
    fbp_style = [f'{c}{fbp_linestyle}' for c in colors]
    proc_style = [f'{c}{proc_linestyle}' for c in colors]
    fbp_df.plot(ax=ax, style=fbp_style)
    proc_df.plot(ax=ax, style=proc_style)
    ax.set_title(title)
    ax.set_xlabel('distance [pixels]')
    ax.set_ylabel('CT Number [HU]')
    if legend:
        ax.legend(custom_lines, ['FBP', 'REDCNN'])
    else:
        ax.get_legend().remove()
    return ax