import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def plot_patient_diameter_mtf(mtf_csv_fname, patient_diameter:str=None, ax=None):
    if ax is None:
        f, ax = plt.subplots()
    
    mtf_csv_fname = Path(mtf_csv_fname)
    patient_diameter_dir = mtf_csv_fname.parents[1]
    diameter = patient_diameter_dir.stem.split('diameter')[1]
    df = pd.read_csv(mtf_csv_fname)
    freq_lpcm_lbl = 'frequencies [lp/cm]'
    df[freq_lpcm_lbl] = df['frequencies [1/mm]']*10
    HUs = sorted([int(h.split(' HU')[0]) for h in df.columns[1:-1]])
    cols = [freq_lpcm_lbl]
    cols += [f' {h} HU' for h in HUs]
    df = df[cols]
    df.plot(ax=ax, x=freq_lpcm_lbl, xlim=[0, 20], title=diameter, ylabel='MTF')
    return ax