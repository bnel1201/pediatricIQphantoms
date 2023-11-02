import argparse
from pathlib import Path

import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import h5py

import matplotlib.patches as patches

import pandas as pd
import seaborn as sns


def load_adult_dataset_from_matfiles(basedir=None, recon='cnn', dose_idx=-1):
    basedir = basedir or Path('/gpfs_projects/prabhat.kc/lowdosect/transfers/transfers_4_spie/exps/quant_analysis/mita_lcd/results/95d_2_75d_2_25d_p96_no_norm/no_norm/redcnn/augTrTaTdT/')
    aucs = []
    recon_idx = 1 if recon=='cnn' else 0
    for i in range(4):
        data = scipy.io.loadmat(basedir / f'_idx_{i+1}.mat')
        aucs.append(data['auc_all'][:][:, recon_idx, dose_idx]) #get last dose level (highest)
    return np.stack(aucs)

def load_all_adult_data_from_matfiles():
    basedir = Path("/gpfs_projects/prabhat.kc/lowdosect/transfers/transfers_4_spie/exps/quant_analysis/mita_lcd")
    resultsdir = basedir / "results/quarter/8p_uni_norm/dncnn/augTrTaTdT/"
    nreaders = 10
    ndose_levels = 5
    nrecons = 2
    nlesions = 4
    aucs = np.zeros([nreaders, ndose_levels, nrecons, nlesions])
    for dose_idx in range(ndose_levels):
        for recon_idx, recon in enumerate(['fbp', 'cnn']):
            aucs[:, dose_idx, recon_idx, :] = load_adult_dataset_from_matfiles(resultsdir, dose_idx=dose_idx, recon=recon).T
    return aucs


def convert_original_adult_matfiles_to_h5(results_dir):
    aucs = load_all_adult_data_from_matfiles()
    adult_ref_h5file = f'{results_dir}/adult_ref_LCD_results.h5'
    with h5py.File(adult_ref_h5file, 'w') as f:
        auc_dset = f.create_dataset('auc', aucs.shape, aucs.dtype)
        auc_dset[...] = aucs

        fov_dset = f.create_dataset('fov_size_mm', (1,), aucs.dtype)
        fov_dset[...] = 212.48

        dose_dset = f.create_dataset('dose_levels', (5,), '<f8')
        dose_dset[...] = [90000, 165000, 210000, 255000, 300000]

        inserts_dset = f.create_dataset('insert_HUs', (4,), '<f8')
        inserts_dset[...] = [14, 7, 5, 3]

        recon_type_dset = f.create_dataset('recon_types', (2,), 'S10')
        recon_type_dset[...] = ['fbp', 'dl_REDCNN']
    return adult_ref_h5file


# lesion_HUs = [14, 7, 5, 3]
# lesion_diameter_mm = [3, 5, 7, 10]


# def get_auc_df(ped_h5file, adult_h5file lesion_idx=0, recon='fbp'):







#     recon_idx = 0 if recon=='fbp' else 1
#     ped_fbp_auc = pd.DataFrame(auc_mean[:, recon_idx, lesion_idx, :], columns = diameters)
#     ped_fbp_auc['Dose Level [%]'] = dose_levels_pct
#     ped_fbp_auc.set_index('Dose Level [%]', inplace=True)

#     adult_fbp_auc = pd.DataFrame(adult_auc_means[:, 0, lesion_idx], columns = [200])
#     adult_fbp_auc['Dose Level [%]'] = dose_levels_pct
#     adult_fbp_auc.set_index('Dose Level [%]', inplace=True)
#     auc = ped_fbp_auc.join(adult_fbp_auc)
#     return auc


def make_auc_heatmap_grid(h5file, recon_type='fbp'):
    f, axs = plt.subplots(2, 2, figsize=(12,10),gridspec_kw=dict(hspace=0.4, wspace=0.2))
    for lesion_idx, (ax, lesion_hu, lesion_diam) in enumerate(zip(axs.flatten(), lesion_HUs, lesion_diameter_mm)):

        if recon_type == 'diff':
            auc =  get_auc_df(h5file, lesion_idx, 'cnn') - get_auc_df(h5file, lesion_idx, 'fbp')
        else:
            auc = get_auc_df(h5file, lesion_idx, recon_type)

        sns.heatmap(auc, annot=True, ax=ax, cbar_kws=dict(label=f'AUC'))
        ax.set_xlabel('Patient Diameter [mm]')
        twiny = ax.twiny()

        fovs = np.round(auc.columns*1.1).astype(int).to_list()
        fovs[auc.columns.to_list().index(200)] = 212 # From RZ, min FOV for adult scan protocol
        twiny.set_xticks(ax.get_xticks(), fovs)
        twiny.set_xlim(ax.get_xlim())
        twiny.set_xlabel("Recon FOV [mm]")
        twiny.grid(False)
        nrows = len(auc)
        rect = patches.Rectangle((6, 0.05), 0.97, nrows-0.1, linewidth=3, edgecolor='tab:blue', facecolor='none')
        ax.annotate("Adult Reference",
                    xy=(6.75, nrows), xycoords='data',
                    xytext=(0.75, 0.025), textcoords='figure fraction',
                    color='tab:blue',
                    arrowprops=dict(facecolor='tab:blue', shrink=0.05), weight='bold')
        ax.add_patch(rect)
        ax.set_title(f'{lesion_diam} mm, {lesion_hu} HU')
    f.suptitle(recon_type)
    return f, axs

def main(results_dir, reference_diameter=200):
    """
    Dimensions of AUC results array are [reader num, dose level, recon option, inserts num, patient diameter] 
    These are reversed from matlab which is F index, but Python is C indexed
    """

    # load peds results
    # results_dir = '../../results/LCD'
    ped_h5file = Path(results_dir) / 'LCD_results.h5'
    f = h5py.File(ped_h5file, 'r')
    auc = f['auc'][:]
    snr = f['snr'][:]
    diameters = f['patient_diameters'][:].astype(int)
    dose_levels = f['dose_levels'][:]
    dose_levels_pct = np.ceil(dose_levels / dose_levels.max()*100)
    # lesion_HUs = f['insert_HUs']
    lesion_HUs = [14, 7, 5, 3]
    lesion_radii_mm = [3, 5, 7, 10]
    lesion_radii_pix = [2.30, 3.99, 5.57, 7.97]
    recon_types = list(map(lambda x: x.decode('UTF-8'), f['recon_types'][:]))
    nreaders = f['readers'][:]
    f.close()

    auc_mean, auc_std = auc.mean(axis=0), auc.std(axis=0)
    snr_mean, snr_std = snr.mean(axis=0), auc.std(axis=0)


    # load adults results
    # adult_h5file = f'{results_dir}/adult_ref_LCD_results.h5' # <-old indexing method
    # adult_h5file = '/home/brandon.nelson/Data/temp/CCT189/rz_results/LCD_results_orig.h5'
    # adult_h5file = '/home/brandon.nelson/Data/temp/CCT189/rz_results/LCD_results.h5'
    # with h5py.File(adult_h5file, 'r') as f:
    #     adult_auc = f['auc'][:]
    #     adult_snr = f['snr'][:]
    # if adult_auc.shape[0] != 10:
    #     adult_auc = adult_auc.transpose([2, 0, 1, 3])
    #     adult_snr = adult_snr.transpose([2, 0, 1, 3])
    # adult_dose_level_pct = [30, 55, 70, 85, 100]
    # adult_auc_means, adult_auc_stds = adult_auc.mean(axis=0), adult_auc.std(axis=0)
    # adult_snr_means, adult_snr_stds = adult_snr.mean(axis=0), adult_snr.std(axis=0)
    ref_idx = np.where(diameters==reference_diameter)[0][0]
    adult_diameter = diameters[ref_idx]
    diameters = np.delete(diameters, ref_idx)
    adult_auc_means, adult_auc_stds = auc_mean[:, :, :, ref_idx], auc_std[:, :, :, ref_idx]
    adult_snr_means, adult_snr_stds = snr_mean[:, :, :, ref_idx], snr_std[:, :, :, ref_idx]
    auc_mean, auc_std = np.delete(auc_mean, ref_idx, -1), np.delete(auc_std, ref_idx, -1)
    snr_mean, snr_std = np.delete(snr_mean, ref_idx, -1), np.delete(snr_std, ref_idx, -1)
   

    # ***Be sure to remove the ref_idx from auc and snr mean!!! <----***
    # %%
    # dose_idx=0
    recon_idx=recon_types.index('fbp')
    lesion_idxs = [0, 1, 3, 2]

    sns.set_style("darkgrid")
    # sns.set_context("talk")
    fbp_idx = recon_types.index('fbp')
    cnn_idx = recon_types.index('dl_REDCNN')
    ## auc diff
    diam_idx = [0, 2, -1]
    diam_idx = range(len(diameters))
    fig, axs = plt.subplots(2, 2, figsize=(6,6), sharex=True, sharey=True)
    subplot_idx = 0
    dose_levels_pct = np.ceil(dose_levels / dose_levels.max()*100)
    for lesion_idx, ax in zip(lesion_idxs , axs.flatten()):
        auc_mean_diff = auc_mean[:, cnn_idx, lesion_idx, diam_idx]-auc_mean[:, fbp_idx, lesion_idx, diam_idx]
        auc_std_diff = np.sqrt(auc_std[:, cnn_idx, lesion_idx, diam_idx]**2 + auc_std[:, fbp_idx, lesion_idx, diam_idx]**2) # <-- I think you do pythagorean add (sqrt(std1^2 + std2^2))

        # auc_mean_diff = auc_mean[:, cnn_idx, lesion_idx, diam_idx]/auc_mean[:, fbp_idx, lesion_idx, diam_idx]
        # auc_std_diff = np.sqrt((auc_std[:, cnn_idx, lesion_idx, diam_idx]/auc_mean[:, cnn_idx, lesion_idx, diam_idx])**2 + (auc_std[:, fbp_idx, lesion_idx, diam_idx]/auc_mean[:, fbp_idx, lesion_idx, diam_idx])**2) # <-- I think you do pythagorean add (sqrt(std1^2 + std2^2))

        if subplot_idx > 1:
            ax.set_xlabel('Dose Level [%]')
        for d in diam_idx:
            ax.errorbar(dose_levels_pct, auc_mean_diff[:, d], yerr=auc_std_diff[:, d], label=f'{diameters[d]}')
            # ax.plot(dose_levels_pct, auc_mean_diff[:, d], label=f'{diameters[d]:0.0f} mm')
            ax.set_title(f'{lesion_radii_mm[lesion_idx]} mm diameter\n{lesion_HUs[lesion_idx]} HU disk')
            if not subplot_idx % 2:
                ax.set_ylabel('Difference in Detectability\nREDCNN - FBP [AUC]')
        if subplot_idx < 1:
            ax.legend()
        subplot_idx+=1
    fig.tight_layout()
    output_fname = Path(results_dir) / 'auc_diffs_.png'
    fig.savefig(output_fname, dpi=600)
    print(f"filed saved: {output_fname}")
    ## snr diff
    fig, axs = plt.subplots(2, 2, figsize=(6,6), sharex=True, sharey=True)
    subplot_idx = 0
    dose_levels_pct = np.ceil(dose_levels / dose_levels.max()*100)
    for lesion_idx, ax in zip(lesion_idxs , axs.flatten()):
        snr_mean_diff = snr_mean[:, cnn_idx, lesion_idx, diam_idx]-snr_mean[:, fbp_idx, lesion_idx, diam_idx]
        snr_std_diff = np.sqrt(snr_std[:, cnn_idx, lesion_idx, diam_idx]**2 + snr_std[:, fbp_idx, lesion_idx, diam_idx]**2) # <-- I think you do pythagorean add (sqrt(std1^2 + std2^2))

        # snr_mean_diff = snr_mean[:, cnn_idx, lesion_idx, diam_idx]/snr_mean[:, fbp_idx, lesion_idx, diam_idx]
        # snr_std_diff = np.sqrt((snr_std[:, cnn_idx, lesion_idx, diam_idx]/snr_mean[:, cnn_idx, lesion_idx, diam_idx])**2 + (snr_std[:, fbp_idx, lesion_idx, diam_idx]/snr_mean[:, fbp_idx, lesion_idx, diam_idx])**2) # <-- I think you do pythagorean add (sqrt(std1^2 + std2^2))

        # auc_std_diff = auc_std[:, cnn_idx, lesion_idx, diam_idx]-auc_std[:, fbp_idx, lesion_idx, diam_idx]

        if subplot_idx > 1:
            ax.set_xlabel('Dose Level [%]')
        for d in diam_idx:
            ax.errorbar(dose_levels_pct, snr_mean_diff[:, d], yerr=snr_std_diff[:, d], label=f'{diameters[d]}')
            # ax.plot(dose_levels_pct, snr_mean_diff[:, d], label=f'{diameters[d]:0.0f} mm')
            ax.set_title(f'{lesion_radii_mm[lesion_idx]} mm diameter\n{lesion_HUs[lesion_idx]} HU disk')
            if not subplot_idx % 2:
                ax.set_ylabel('Difference in AUC SNR\nREDCNN - FBP [AUC SNR]')
        if subplot_idx < 1:
            ax.legend()
        subplot_idx+=1
    fig.tight_layout()
    output_fname = Path(results_dir) / 'auc_snr_diffs_.png'
    fig.savefig(output_fname, dpi=600)
    print(f"filed saved: {output_fname}")

    fbp_idx = recon_types.index('fbp')
    cnn_idx = recon_types.index('dl_REDCNN')

 ## auc
    output_dir = Path(results_dir) / 'plots' / 'auc'
    output_dir.mkdir(exist_ok=True, parents=True)
    for diam_idx, d in enumerate(diameters):
        fig, axs = plt.subplots(2, 2, figsize=(6,6), sharex=True, sharey=True)
        subplot_idx = 0
        dose_levels_pct = np.ceil(dose_levels / dose_levels.max()*100)
        for lesion_idx, ax in zip(lesion_idxs , axs.flatten()):

            if subplot_idx > 1:
                ax.set_xlabel('Dose Level [%]')
            # for d in diam_idx:
            ax.errorbar(dose_levels_pct, auc_mean[:, fbp_idx, lesion_idx, diam_idx], yerr=auc_std[:, fbp_idx, lesion_idx, diam_idx], label=f'FBP')
            ax.errorbar(dose_levels_pct, auc_mean[:, cnn_idx, lesion_idx, diam_idx], yerr=auc_std[:, cnn_idx, lesion_idx, diam_idx], label=f'REDCNN')
            ax.errorbar(dose_levels_pct , adult_auc_means[:, fbp_idx, lesion_idx],
                        yerr=adult_auc_stds[:, fbp_idx, lesion_idx],
                        fmt='--', markersize=10,
                        color='black', label='Adult FBP\n(212 mm FOV)')
            ax.errorbar(dose_levels_pct, adult_auc_means[:, cnn_idx, lesion_idx],
                        yerr=adult_auc_stds[:, cnn_idx, lesion_idx],
                        fmt='--', markersize=10,
                        color='gray', label='Adult REDCNN\n(212 mm FOV)')
            # ax.plot(dose_levels_pct, auc_mean_diff[:, d], label=f'{diameters[d]:0.0f} mm')
            ax.set_title(f'{lesion_radii_mm[lesion_idx]} mm diameter\n{lesion_HUs[lesion_idx]} HU disk')
            if not subplot_idx % 2:
                ax.set_ylabel('Detectability AUC')
            if subplot_idx < 1:
                ax.legend(loc = 'lower right', fontsize=6)
            subplot_idx+=1
            ax.set_ylim([0.65, 1])
        output_fname = output_dir / f'AUC_v_dose_diameter_{d}mm.png'
        fig.suptitle(f'Patient Diameter: {diameters[diam_idx]:0.0f} mm (FOV: {diameters[diam_idx]*1.1:0.0f} mm)')
        fig.savefig(output_fname, dpi=600)
        print(f"filed saved: {output_fname}")
    
     ## snr
    output_dir = Path(results_dir) / 'plots' / 'snr'
    output_dir.mkdir(exist_ok=True, parents=True)
    for diam_idx, d in enumerate(diameters):
        fig, axs = plt.subplots(2, 2, figsize=(6,6), sharex=True, sharey=True)
        subplot_idx = 0
        dose_levels_pct = np.ceil(dose_levels / dose_levels.max()*100)
        for lesion_idx, ax in zip(lesion_idxs , axs.flatten()):

            if subplot_idx > 1:
                ax.set_xlabel('Dose Level [%]')
            # for d in diam_idx:
            ax.errorbar(dose_levels_pct, snr_mean[:, fbp_idx, lesion_idx, diam_idx], yerr=snr_std[:, fbp_idx, lesion_idx, diam_idx], label=f'FBP')
            ax.errorbar(dose_levels_pct, snr_mean[:, cnn_idx, lesion_idx, diam_idx], yerr=snr_std[:, cnn_idx, lesion_idx, diam_idx], label=f'REDCNN')
            ax.errorbar(dose_levels_pct , adult_snr_means[:, fbp_idx, lesion_idx],
                        yerr=adult_snr_stds[:, fbp_idx, lesion_idx],
                        fmt='--', markersize=10,
                        color='black', label='Adult FBP\n(212 mm FOV)')
            ax.errorbar(dose_levels_pct , adult_snr_means[:, cnn_idx, lesion_idx],
                        yerr=adult_snr_stds[:, cnn_idx, lesion_idx],
                        fmt='--', markersize=10,
                        color='gray', label='Adult REDCNN\n(212 mm FOV)')
            # ax.plot(dose_levels_pct, auc_mean_diff[:, d], label=f'{diameters[d]:0.0f} mm')
            ax.set_title(f'{lesion_radii_mm[lesion_idx]} mm diameter\n{lesion_HUs[lesion_idx]} HU disk')
            if not subplot_idx % 2:
                ax.set_ylabel('AUC SNR')
            if subplot_idx < 1:
                ax.legend(loc = 'lower right', fontsize=6)
            subplot_idx+=1
            ax.set_ylim([-1, 9])
        output_fname = output_dir / f'AUC_SNR_v_dose_diameter_{d}mm.png'
        fig.suptitle(f'Patient Diameter: {diameters[diam_idx]:0.0f} mm (FOV: {diameters[diam_idx]*1.1:0.0f} mm)')
        fig.savefig(output_fname, dpi=600)
        print(f"filed saved: {output_fname}")
        # %% [markdown]
        # experimenting with 2D display

        # # %%
        # f, axs = make_auc_heatmap_grid('fbp')
        # # %%
        # f, axs = make_auc_heatmap_grid('cnn')
        # # %%
        # f, axs = make_auc_heatmap_grid('diff')
        # # %%
    # #  %%
    # main('../../results/LCD')
    # # %%
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plots LCD results')
    parser.add_argument('resultsdir',
                        help="directory containing LCD_results.h5 file")
    args = parser.parse_args()
    main(args.resultsdir)