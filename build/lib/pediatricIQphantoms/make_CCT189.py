# %%
from oct2py import octave
import matplotlib.pyplot as plt

def mita_lcd(patient_diameter=200, reference_diameter=200, reference_fov=340, I0=3e5, nb=900, na=580, ds=1, sid=595, sdd=1085.6, offset_s=1.25, down=1, has_bowtie=False, add_noise=True, aec_on=True, nx=512, fov=340, fbp_kernel='hanning,2.05', nsims=1, relative_lesion_diameter=False):

    if patient_diameter == reference_diameter:
        fov = reference_fov
    else:
        fov = 1.1*patient_diameter

    return octave.ct_sim_mitalcd(patient_diameter, reference_diameter,    relative_lesion_diameter, I0, nb, na, ds, sdd, sid, offset_s, down, has_bowtie, add_noise, aec_on, nx, fov, fbp_kernel, nsims)

# %%
if __name__ == '__main__':
    res = mita_lcd(I0=3e7, nx=256, has_bowtie=True, patient_diameter=200, fov=250, na=500, relative_lesion_diameter=False)# %%
    vol = res['recon']

    plt.imshow(vol[0], vmin=-10, vmax=20, cmap='gray')
    plt.colorbar()
