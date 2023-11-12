# %%
# https://realpython.com/python-toml/
# %%
import argparse
import tomli
import numpy as np
import os

def main(config):

    image_directory = os.path.abspath(config['directories']['image_directory'])

    phantoms = config['phantoms']['model']

    dose_level = config['acquisition']['full_dose'] * np.array(config['acquisition']['dose_level'])

    matlab_error_status = os.system("matlab -batch version")

    if matlab_error_status:
        print('matlab not install, using Octave')
        interpreter = 'octave --eval'
    else:
        interpreter = 'matlab -batch -noFigureWindows -nosplash' #https://www.mathworks.com/help/matlab/ref/matlabwindows.html


    for phantom_idx, phantom in enumerate(phantoms):
        print(f'{phantom} Simulation series {phantom_idx}/{len(phantoms)}')

        cmd = f"""
        {interpreter} "basedataFolder='{image_directory}';\
        nsims={config['acquisition']['nsims']};\
        image_matrix_size={config['reconstruction']['image_matrix_size']};\
        nangles={config['acquisition']['nangles']};\
        patient_diameters={config['phantoms']['diameter']};\
        aec_on={str(config['acquisition']['aec_on']).lower()};\
        add_noise={str(config['acquisition']['add_noise']).lower()};\
        fbp_kernel='{config['reconstruction']['fbp_kernel']}';\
        reference_dose_level={dose_level};\
        reference_diameter={config['phantoms']['reference_diameter']};\
        reference_fov={config['reconstruction']['fov']};\
        offset={config['reconstruction']['offset']};\
        run('make_phantoms/{phantom}/make_{phantom}.m');\
        exit;"
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
    main(config)
