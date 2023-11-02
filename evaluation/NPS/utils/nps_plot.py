import pandas as pd
import matplotlib.pyplot as plt


def plot_1D_nps(fbp_dir, proc_dir, fig=None, ax=None):
    fbp_nps_df = pd.read_csv(fbp_dir / '1D_nps.csv')
    proc_nps_df = pd.read_csv(proc_dir / '1D_nps.csv')
    if ax is None or fig is None:
        fig, ax = plt.subplots()
    fbp_nps_df.plot(ax=ax, x='spatial frequency [cyc/pix]', y=' magnitude', label='FBP')
    proc_nps_df.plot(ax=ax, x='spatial frequency [cyc/pix]', y=' magnitude', label='REDCNN')