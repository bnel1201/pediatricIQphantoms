import numpy as np
import pandas as pd


def imread(fname, sz=512, dtype=np.int16): return np.fromfile(open(fname), dtype=dtype, count=sz*sz).reshape(sz, sz)


def get_2D_nps_img(nps_dir):
    raw_fname=next(nps_dir.glob('2D_nps_*.raw'))
    sz = int(raw_fname.stem.split('_')[-1])
    return imread(raw_fname, sz=sz, dtype=np.float32)


def get_img_sz(img_dir):
    temp_df = pd.read_csv(img_dir.parents[1] / 'geometry_info.csv').T
    ig = pd.DataFrame({col: [rows] for col, rows in zip(temp_df.iloc[0, :], temp_df.iloc[1, :])})
    nx = int(ig.ny)
    return nx


def get_img(img_dir):
    sz = get_img_sz(img_dir)
    fname =  np.random.choice(list(img_dir.glob('*.raw')), 1)[0]
    return imread(fname, sz=sz, dtype=np.int16)
