import argparse
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

insert_HU_size = {14 : '3 mm', 7: '5 mm', 5: '7 mm', 3: '10 mm'}

def age_to_eff_diameter(age):
    # https://www.aapm.org/pubs/reports/rpt_204.pdf
    x = age
    a = 18.788598
    b = 0.19486455
    c = -1.060056
    d = -7.6244784
    y = a + b*x**1.5 + c *x**0.5 + d*np.exp(-x)
    eff_diam = y
    return eff_diam

def plot_insert_level_results(img_level_mean, img_level_std, observers, insert_HUs, ylabel, fig=None, legend_loc='upper left'):
    fig = fig or plt.figure()
    if len(insert_HUs) > 2:
        axs = fig.subplots(2,2, sharex=True, sharey=True).flatten()
    elif len(insert_HUs) == 2:
        axs = fig.subplots(1,2, sharex=True, sharey=True)
    elif len(insert_HUs) == 1:
        axs = [fig.subplots(1,1, sharex=True, sharey=True)]

    plt_idx=0
    for insert_HU, ax in zip(insert_HUs, axs):
        for observer in observers:
            series_mean = img_level_mean[insert_HU, observer]
            series_std = img_level_std[insert_HU, observer]
            series_mean.plot(ax=ax, yerr=series_std, label=observer, capsize=3)
        ax.set_title(f'{insert_HU} HU, {insert_HU_size[insert_HU]}')
        ax.set_ylabel(ylabel)

        if bool(legend_loc) & (plt_idx < 1):
            fig.legend(bbox_to_anchor=(0.5, 1.1), loc = legend_loc, frameon=False, ncol=3)
        plt_idx += 1
    return fig, axs

class LCD_Plotter:
    def __init__(self, lcd_data):
        self.data = lcd_data
        self.reset()
        
    def reset(self):
        self.observers = self.data['observer'].unique()
        self.phantom_diameters = self.data['phantom diameter [mm]'].unique()
        self.insert_HUs = self.data['insert_HU'].unique()
        self.recons = self.data['recon'].unique()
        self.dose_levels = self.data['dose [%]'].unique()

    def plot(self, x='dose', restype='auc', recon_cmp_method='diff', transpose=False):
        if x == 'dose':
            row_data = self.phantom_diameters
        elif x == 'diameter':
            row_data = self.dose_levels
        recons = self.recons
        if not isinstance(row_data, list): row_data = np.array([row_data])
        if not isinstance(recons, list): recons = np.array([recons])
        nrecons = len(recons)

        figsize =  (3*len(row_data) + 1, 3*nrecons + 1) if transpose else (3*nrecons + 1, 3*len(row_data) + 1)
        master_fig = plt.figure(constrained_layout=True, figsize=figsize, dpi=150)
        figs = master_fig.subfigures(nrecons, len(row_data)) if transpose else master_fig.subfigures(len(row_data), nrecons)
        if nrecons + len(row_data) <= 2:
            figs = np.array(figs)
        figs = figs.T.flatten() if transpose else figs.flatten()
        fig_idx = 0
        fig_dict = {}

        for rd in row_data:
            for recon in recons:
                if fig_idx == 0:
                    legend_loc = 'upper left' if transpose else 'upper center'
                else:
                    legend_loc = False
                fig = figs[fig_idx]
                fig, axs = self.plot_img_level_results(rd, x=x, recontype=recon, restype=restype, fig=fig, legend_loc=legend_loc, recon_cmp_method=recon_cmp_method)
                fig_dict[f'fig{fig_idx}'] = [fig, axs] 
                fig_idx += 1
        return fig_dict
        
    def plot_img_level_results(self, row_data, x='dose', recontype='fbp', restype='auc', fig=None, legend_loc='upper center', recon_cmp_method='diff'):
        if x == 'dose':
            grouped = self.data.groupby(["phantom diameter [mm]","recon", "insert_HU", "observer", "dose [%]"])
            fig_title = f'{row_data} mm\n'
        elif x == 'diameter':
            grouped = self.data.groupby(["dose [%]", "recon", "insert_HU", "observer", "phantom diameter [mm]"])
            fig_title = f'{row_data}% dose\n'
        lcd_mean = grouped.mean()
        lcd_std = grouped.std()
        
        fig = fig or plt.figure()
        ylabel = f'{restype.upper()}'
        if restype == 'snr': ylabel = "$d'_{" + ylabel + "}$"
        
        insert_HUs = self.insert_HUs
        if isinstance(insert_HUs, int): insert_HUs = [insert_HUs]
        if isinstance(recontype, str):
            img_level_mean = lcd_mean[restype][row_data, recontype]
            img_level_std = lcd_std[restype][row_data, recontype]
            fig_title += f'{recontype}'
        else:
            dlir_mean = lcd_mean[restype][row_data, recontype[0]]
            dlir_std = lcd_std[restype][row_data, recontype[0]]
            fbp_mean = lcd_mean[restype][row_data, recontype[1]]
            fbp_std = lcd_std[restype][row_data, recontype[1]]
            if recon_cmp_method == 'diff':
                img_level_mean = dlir_mean - fbp_mean
                img_level_std = np.sqrt(fbp_std**2 + dlir_std**2)
                fig_title += f'{ylabel}{recontype[0].upper()}-{ylabel}{recontype[1].upper()}'
                ylabel = '$\Delta$' + ylabel
            elif recon_cmp_method == 'div':
                img_level_mean  = dlir_mean / fbp_mean
                img_level_std = np.sqrt((fbp_std/fbp_mean)**2 + (dlir_std/dlir_mean)**2)
                fig_title += f'{ylabel}{recontype[0].upper()}/{ylabel}{recontype[1].upper()}'
                ylabel +=  ' ratio'

        fig.suptitle(fig_title)

        fig, axs = plot_insert_level_results(img_level_mean, img_level_std, self.observers, insert_HUs, ylabel, fig=fig, legend_loc=legend_loc)
        return fig, axs

    
def main(results_csv=None, outputdir=None, restype='auc', comparator='diff'):
    plt.style.use('seaborn-deep')
    results_csv = results_csv or '/home/brandon.nelson/Dev/DLIR_Ped_Generalizability/geometric_phantom_studies/results/LCD/LCD_results.csv'
    results_csv = Path(results_csv)
    outputdir = outputdir or results_csv.parent
    outputdir = Path(outputdir)
    lcd_data = pd.read_csv(results_csv)

    lcd_data.replace({'dl_REDCNN': 'dlir',
                      'NPW 2D': 'NPW', 
                      'Laguerre-Gauss CHO 2D': 'Laguerre-Gauss CHO'}, inplace=True)
    lcd_data.rename(columns={'patient_diameter_mm': 'phantom diameter [mm]', 'dose_level_pct': 'dose [%]'}, inplace=True)
    lcd_data = lcd_data[lcd_data['phantom diameter [mm]'] != 200] #ref has large fov
    plotter = LCD_Plotter(lcd_data)

    plotter.insert_HUs = 7
    plotter.dose_levels = [25]
    plotter.recons = [['dlir', 'fbp']]
    plotter.observers = ['NPW'] # 'Laguerre-Gauss CHO 2D', 'NPW 2D'
    # plotter.observers = ['Laguerre-Gauss CHO'] # 'Laguerre-Gauss CHO 2D', 'NPW 2D'
    fig_dict = plotter.plot(restype=restype, x='diameter', recon_cmp_method=comparator, transpose=False)
    # fig_dict['fig0'][1][0].set_ylim((-0.1, 0.4))
    fig_dict['fig0'][1][0].set_xlim((105, 308))
    fig_dict['fig0'][0].suptitle('')
    fig_dict['fig0'][1][0].set_title('')

    ages = [1, 5, 10, 15, 18]
    axs = [fig_dict['fig0'][1][0]]
    age_yloc = -0.075
    for ax in axs:
        ax.annotate('Age groups with\ncorresponding mean\nabdomen diameter', xy=(170, -0.08), xytext=(110, 0.2), arrowprops=dict(facecolor='black', shrink=0.2, alpha=0.25), fontsize=10)
        for a in ages:
            eff_diam = age_to_eff_diameter(a)*10
            ax.annotate(f'{a}yrs', xy=(eff_diam, age_yloc), xycoords='data', xytext=(eff_diam, age_yloc), ha='center', textcoords='data')

    f = plt.gcf()
    f.set_figheight(2)
    f.set_figwidth(3.2)
    output_fname = outputdir/f"{restype.upper()}_{comparator}_v_diameter.png"
    plt.savefig(output_fname, dpi=600, bbox_inches="tight")
    print(f'file saved: {output_fname}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plots LCD images from CCT189')
    parser.add_argument('csvfile', nargs='?', default=None)
    parser.add_argument('--output_dir','-o', required=False,
                    help="Directory to save image files")
    args = parser.parse_args()
    main(args.csvfile, args.output_dir)