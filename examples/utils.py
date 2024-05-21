import pydicom
import matplotlib.pyplot as plt
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

def browse_studies(metadata, phantom='CTP404', fov=12.3, dose=100, recon='fbp', kernel='D45', repeat=0, display='soft tissues'):
    phantom_df =  metadata[(metadata.phantom==phantom)]
    available_fovs = sorted(phantom_df['FOV [cm]'].unique())
    if fov not in available_fovs:
        print(f'FOV {fov} not in {available_fovs}')
        return
    available_doses = sorted(phantom_df['Dose [%]'].unique())
    if dose not in available_doses:
        print(f'dose {dose}% not in {available_doses}')
        return
    patient = phantom_df[(phantom_df['phantom'] == phantom) &
                       (phantom_df['recon'] == recon) &
                       (phantom_df['FOV [cm]']==fov)]
    if recon != 'ground truth':
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