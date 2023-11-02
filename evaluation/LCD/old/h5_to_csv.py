import h5py
import pandas as pd
import argparse


def main(in_h5file, out_csvfile):
    with h5py.File(in_h5file, 'r') as f:
        data = {k: f[k][:] for k in f.keys()}

    patient_diameters = []
    recon_types = []
    dose_levels = []
    fov_size_mm = []
    vox_size_mm = []
    insert_radii_pix = []
    insert_HUs = []
    readers = []
    auc = []
    snr = []

    for p_idx, p in enumerate(data['patient_diameters']):
        for d_idx, d in enumerate(data['dose_levels']):
            for t_idx, t in enumerate(data['recon_types']):
                for h_idx, h in enumerate(data['insert_HUs']):
                    for r_idx in range(int(data['readers'][0])):
                        patient_diameters.append(int(p))
                        recon_types.append(t.astype(str))
                        dose_levels.append(int(d))
                        fov_size_mm.append(data['fov_size_mm'][p_idx])
                        vox_size_mm.append(data['vox_size_mm'][p_idx])
                        insert_radii_pix.append(data['insert_radii_pix'][h_idx])
                        insert_HUs.append(int(h))
                        readers.append(r_idx)
                        auc.append(data['auc'][r_idx, d_idx, t_idx, h_idx, p_idx])
                        snr.append(data['snr'][r_idx, d_idx, t_idx, h_idx, p_idx])

    lcd_data = pd.DataFrame({
        'patient diameter [mm]': patient_diameters,
        'fov [mm]': fov_size_mm,
        'voxel size [mm]': vox_size_mm,
        'dose level [photons]': dose_levels,
        'recon type': recon_types,
        'lesion contrast [HU]': insert_HUs,
        'lesion radius [pixels]': insert_radii_pix,
        'reader': readers,
        'auc': auc,
        'snr': snr
    })
    lcd_data.replace('dl_REDCNN', 'cnn', inplace=True)
    lcd_data.to_csv(out_csvfile, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='for converting h5 file from matlab eval_lcd_catSim.m to clean csv file more convenient for pandas analysis')
    parser.add_argument('input',
                        help='input .h5 file')
    parser.add_argument('-o', '--output',
                        help='output csv filename to be created')
    args = parser.parse_args()
    main(args.input, args.output)
