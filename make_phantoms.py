# %%
# https://realpython.com/python-toml/
# %%
import argparse
import tomli
import numpy as np
import os

def main(config):

    image_directory = os.path.abspath(config['image_directory'])

    phantoms = config['model']

    dose_level = config['full_dose'] * np.array(config['dose_level'])

    matlab_error_status = os.system("matlab -batch version")

    if matlab_error_status:
        print('matlab not install, using Octave')
        interpreter = 'octave --eval'
    else:
        interpreter = 'matlab -batch' #https://www.mathworks.com/help/matlab/ref/matlabwindows.html
        # -batch doesnt work for matlab here so revert to old -r flag
    for phantom_idx, phantom in enumerate(phantoms):
        print(f'{phantom} Simulation series {phantom_idx}/{len(phantoms)}')

        cmd = f"""
               {interpreter} "basedataFolder='{image_directory}';\
               nsims={config['nsims']};\
               image_matrix_size={config['image_matrix_size']};\
               nangles={config['nangles']};\
               patient_diameters={config['diameter']};\
               aec_on={str(config['aec_on']).lower()};\
               add_noise={str(config['add_noise']).lower()};\
               fbp_kernel='{config['fbp_kernel']}';\
               reference_dose_level={dose_level};\
               reference_diameter={config['reference_diameter']};\
               reference_fov={config['fov']};\
               offset={config['offset']};run('make_phantoms/{phantom}/make_{phantom}.m');exit;"\
               """
        os.system(cmd)
# %%
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make Pediatric IQ Phantoms')
    parser.add_argument('config', nargs='?', default=None,
                        help="configuration toml file containing simulation parameters")
#  TODO add overrides to override anything from the config file by adding keywords to the command line
    args = parser.parse_args()

    if args.config:
        with open(args.config, mode="rb") as fp:
            config = tomli.load(fp)
    else:
        with open("configs/defaults.toml", mode="rb") as fp:
            config = tomli.load(fp)
    
    sim = dict()
    for c in config['simulation']:
        sim.update(c)
        main(sim)
