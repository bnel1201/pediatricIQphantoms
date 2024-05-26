from pathlib import Path

import pydicom
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets import interact

# https://radiopaedia.org/articles/windowing-ct?lang=us
display_settings = {
    'brain': (80, 40),
    'subdural': (300, 100),
    'stroke': (40, 40),
    'temporal bones': (2800, 600),
    'soft tissues': (400, 50),
    'lung': (1500, -600),
    'liver': (150, 30),
}

def ctshow(img, window='soft tissues'):
    # Define some specific window settings here
    if isinstance(window, str):
        if window not in display_settings:
            raise ValueError(f"{window} not in {display_settings}")
        ww, wl = display_settings[window]
    elif isinstance(window, tuple):
        ww = window[0]
        wl = window[1]
    else:
        ww = 6.0 * img.std()
        wl = img.mean()

    if img.ndim == 3: img = img[0].copy()

    plt.imshow(img, cmap='gray', vmin=wl-ww/2, vmax=wl+ww/2)
    plt.xticks([])
    plt.yticks([])
    return


def circle_select(img, xy, r):
    assert(img.ndim == 2)
    circle_mask = np.zeros_like(img)
    for i in range(circle_mask.shape[0]):
        for j in range(circle_mask.shape[1]):
            if (i-xy[0])**2 + (j-xy[1])**2 < r**2:
                 circle_mask[i,j] = True
    return circle_mask.astype(bool)


def make_montage(meta_df:pd.DataFrame, dose:int=25, fovs:list=[25.0, 15.0], recons:list = ['fbp', 'RED-CNN'],
                 phantom:str='uniform', roi_diameter:float=0.4, roi_center:tuple=(256, 256), wwwl=(80, 0)):
    """
    make image montage based on given argument parameters. Recons are plotted horizontally along the x axis while different diameters are plotted on y
    :Parameters:
        :meta_df: metadata dataframe
        :dose: dose level in percent [%]
        :fovss: FOV in cm
        :recons: list of recon kernels to display on the horizontal x-axis
        :phantom: which image phantom is expected ['MITA-LCD', 'uniform', 'anthropomorphic', 'ACR464'], it should be in meta_df
        :roi_diameter: diameter of circlular ROI. If `roi_diameter` is an **integer** then roi_diameter is in pixels e.g. 100, else if `roi_diameter` is **float** e.g. 0.3 then it is assumed a fraction of the phantom's effective diameter. Note for noise measurements IEC standard suggests centred circle ROI 40% of phantom diameter
        :roi_center: xy coordinates for roi center, or organ e.g. liver, if phantom = 'anthropomorphic'. If `str` is provided an is in the organ list `['liver']` a **random** centered roi that fits in the organ will be provided. If `roi_center` is a tuple, e.g. (256, 256) then an roi at those exact coordinates will be given
        :wwwl: window width and window level display settings, examples: soft tissues (400, 50), liver (150, 30) for recommend display settings see <https://radiopaedia.org/articles/windowing-ct?lang=us> for more information
    """
    all_imgs = []
    all_gts = []
    circle_selections = []
    idx = 0
    for fov in fovs:
        recon_imgs = []
        recon_selections = []
        phantom_df =  meta_df[(meta_df.phantom==phantom)]
        available_fovs = sorted(phantom_df['FOV [cm]'].unique())
        if fov not in available_fovs:
            print(f'FOV {fov} not in {available_fovs}')
            return
        phantom_df = phantom_df[phantom_df['FOV [cm]']==fov]
        available_doses = sorted(phantom_df['Dose [%]'].unique())
        if dose not in available_doses:
            print(f'dose {dose}% not in {available_doses}')
            return
        phantom_df = phantom_df[phantom_df['Dose [%]']==dose]

        selection = None
        for recon in recons:
            nfiles = len(phantom_df[phantom_df.recon == recon])
            if nfiles > 1:
                file = phantom_df[phantom_df.recon == recon].iloc[0].file
            elif nfiles == 1:
                file = phantom_df[phantom_df.recon == recon].file.item()
            else:
                raise RuntimeError('No files found')
            dcm = pydicom.read_file(file)
            img = dcm.pixel_array + int(dcm.RescaleIntercept)

            pixel_size_mm = float(dcm.PixelSpacing[0])
            phantom_diameter_mm = float(dcm.ImageComments.split('effctive diameter [cm]:')[1])*10
            phantom_diameter_pixels = phantom_diameter_mm/pixel_size_mm
            roi_radius = phantom_diameter_pixels*roi_diameter/2
            
            selection = circle_select(img, roi_center, r = roi_radius)
            
            recon_imgs.append(img)
            recon_selections.append(selection)

        all_imgs.append(recon_imgs)
        circle_selections.append(recon_selections)
    
    immatrix = np.concatenate([np.concatenate(row, axis=1) for row in all_imgs], axis=0)
    if isinstance(wwwl, str):
        if wwwl not in display_settings:
            raise ValueError(f'{wwwl} not in {display_settings}')
        wwwl = display_settings[wwwl]
    ctshow(immatrix, wwwl)
    plt.colorbar(fraction=0.015, pad=0.01, label='HU')
    immatrix = np.concatenate([np.concatenate(row, axis=1) for row in circle_selections], axis=0)
    plt.imshow(immatrix, alpha=0.1, cmap='Reds')
    for didx, diam in enumerate(all_imgs):
        for ridx, recon in enumerate(diam):
            nx, ny = recon.shape
            plt.annotate(f'mean: {recon[circle_selections[didx][ridx]].mean():2.0f} HU\nstd: {recon[circle_selections[didx][ridx]].std():2.0f} HU',
                         (ny//2 + ny*ridx, nx//2 + nx*didx), fontsize=6, bbox=dict(boxstyle='square,pad=0.3', fc="lightblue", ec="steelblue"))
    plt.title(' | '.join(recons))
    plt.ylabel(' cm |'.join(map(lambda o: str(round(o)), fovs[::-1])) + ' cm')




def diameter_range_from_subgroup(subgroup):
    if subgroup == 'newborn': return (0, age_to_eff_diameter(1/12))
    elif subgroup == 'infant': return (age_to_eff_diameter(1/12), age_to_eff_diameter(2))
    elif subgroup == 'child': return (age_to_eff_diameter(2), age_to_eff_diameter(12))
    elif subgroup == 'adolescent': return (age_to_eff_diameter(12), age_to_eff_diameter(22))
    else: return (age_to_eff_diameter(22), 100)


save_dir = Path('/gpfs_projects/brandon.nelson/RSTs/pediatricIQphantoms')

def browse_studies(metadata, phantom='CTP404', fov=12.3, dose=100, recon='fbp', kernel='D45', repeat=0, display='soft tissues'):
    phantom_df =  metadata[(metadata.phantom==phantom) & (metadata.recon == recon)]
    available_fovs = sorted(phantom_df['FOV [cm]'].unique())
    if fov not in available_fovs:
        print(f'FOV {fov} not in {available_fovs}')
        return
    patient = phantom_df[phantom_df['FOV [cm]']==fov]
    if (recon != 'ground truth') and (recon != 'noise free'):
        available_doses = sorted(patient['Dose [%]'].unique())
        if dose not in available_doses:
            print(f'dose {dose}% not in {available_doses}')
            return
        patient = patient[(patient['Dose [%]']==dose) &
                       (patient['kernel'] == kernel) &
                       (patient['repeat']==repeat)]
    dcm_file = patient.file.item()
    dcm = pydicom.dcmread(dcm_file)
    img = dcm.pixel_array + int(dcm.RescaleIntercept)

    ww, wl = display_settings[display]
    minn = wl - ww/2
    maxx = wl + ww/2
    plt.figure()
    plt.imshow(img, cmap='gray', vmin=minn, vmax=maxx)
    plt.colorbar(label=f'HU | {display} [ww: {ww}, wl: {wl}]')
    plt.title(patient['Name'].item())

def study_viewer(metadata): 
    viewer = lambda **kwargs: browse_studies(metadata, **kwargs)
    interact(viewer,
             phantom=metadata.phantom.unique(),
             dose=sorted(metadata['Dose [%]'].unique(), reverse=True),
             fov=sorted(metadata['FOV [cm]'].unique()),
             recon=metadata['recon'].unique(),
             kernel=metadata['kernel'].unique(),
             repeat=metadata['repeat'].unique(),
             display=display_settings.keys())
    
def measure_roi_std(dcm_file, roi_diameter=0.4):
    """
    :Parameters:
        :dcm_file: dicom filename
        :roi_diameter: diameter of circlular ROI. If `roi_diameter` is an **integer** then roi_diameter is in pixels e.g. 100, else if `roi_diameter` is **float** e.g. 0.3 then it is assumed a fraction of the phantom's effective diameter. Note for noise measurements IEC standard suggests centred circle ROI 40% of phantom diameter
    """
    dcm = pydicom.read_file(dcm_file)
    img = dcm.pixel_array + int(dcm.RescaleIntercept)

    pixel_size_mm = float(dcm.PixelSpacing[0])
    phantom_diameter_mm = float(dcm.ImageComments.split('effctive diameter [cm]:')[1])*10
    phantom_diameter_pixels = phantom_diameter_mm/pixel_size_mm
    roi_radius = phantom_diameter_pixels*roi_diameter/2

    circle_selection = circle_select(img, xy=(img.shape[0]//2, img.shape[1]//2), r=roi_radius)
    return img[circle_selection].std()

def noise_reduction(fbp_std, denoised_std): return 100*(fbp_std - denoised_std)/fbp_std

def calculate_noise_reduction(results, measure='noise std [HU]'):
    cols = ['phantom', 'FOV [cm]', 'recon', 'Dose [%]']
    means = results[[*cols, measure]].groupby(cols).mean()
    noise_reductions = []
    for idx, row in results.iterrows():
        fbp_noise = means[measure][row.phantom, row['FOV [cm]'], 'fbp', row['Dose [%]']]
        noise_reductions.append(noise_reduction(fbp_noise, row[measure]))
    results[f'{measure} reduction [%]'] = noise_reductions
    return results