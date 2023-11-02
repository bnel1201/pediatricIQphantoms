# %%
from pathlib import Path
import scipy.io
import matplotlib.pyplot as plt
import numpy as np
# %%
data = scipy.io.loadmat('/gpfs_projects/prabhat.kc/lowdosect/transfers/transfers_4_spie/exps/quant_analysis/nps/results/water_test/nps_redcnn.mat')
data.keys()
# %%
#  adult cnn images dir </gpfs_projects/prabhat.kc/lowdosect/transfers/transfers_4_spie/exps/quant_analysis/nps/results/water_test/no_norm/redcnn/p96_augTrTaTdT>

adult_nps = data['nps1d'].mean(axis=0)
freq = data['fr'].mean(axis=0)
# %%
plt.plot(freq, adult_nps)
# %%
(np.diff(freq)[0]*adult_nps).sum()
# %%
def imread(fname, sz=512, dtype=np.int16): return np.fromfile(open(fname), dtype=dtype, count=sz*sz).reshape(sz, sz)

def get_noise_level(img_dir, nx=256):
    stds=[imread(img, nx)[nx//2-nx//r:nx//2+nx//r, nx//2-nx//r:nx//2+nx//r].std() for img in img_dir.glob('*.raw') ]
    return np.mean(stds) , np.std(stds)

adult_cnn_img_dir = Path('/gpfs_projects/prabhat.kc/lowdosect/transfers/transfers_4_spie/exps/quant_analysis/nps/results/water_test/no_norm/redcnn/p96_augTrTaTdT/')
adult_fbp_img_dir = Path('/gpfs_projects/prabhat.kc/lowdosect/transfers/transfers_4_spie/exps/quant_analysis/nps/results/water_test/orig_fbp_sharp/')

fbp_noise, _ =  get_noise_level(adult_fbp_img_dir, nx=256)
cnn_noise, _ =  get_noise_level(adult_cnn_img_dir, nx=256)

abs(cnn_noise - fbp_noise)/fbp_noise*100
# %%
img = imread(adult_cnn_img_dir / 'cnn_hd_uniform_fbp_sharp_10.raw', 256)
nx=256
r=4
stds=[imread(img, 256)[nx//2-nx//r:nx//2+nx//r, nx//2-nx//r:nx//2+nx//r].std() for img in adult_cnn_img_dir.glob('*.raw') ]
np.mean(stds) , np.std(stds)
# %%
stds=[imread(img, 256)[nx//2-nx//r:nx//2+nx//r, nx//2-nx//r:nx//2+nx//r].std() for img in adult_fbp_img_dir.glob('*.raw') ]
np.mean(stds) , np.std(stds)
# %%
