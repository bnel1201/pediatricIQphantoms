# %%
from pediatricIQphantoms.make_phantoms import mita_lcd

# %% test recon
matrix_size = 128
nsims = 2
nangles = 100
ndetectors = 400
res = mita_lcd(nx=matrix_size, nsims=nsims, nb=ndetectors, na=nangles)
vol = res['recon']

def test_recon_shape():
    assert vol.shape == (nsims, matrix_size, matrix_size)

def test_sinogram_shape():
    assert res['sinogram_noiseless'].shape == (ndetectors, nangles)

