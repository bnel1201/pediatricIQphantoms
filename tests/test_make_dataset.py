from pathlib import Path
from shutil import rmtree
import tomli
from subprocess import run

config_file = Path('.').absolute().parent  / 'configs/test.toml'

with open(config_file, mode="rb") as fp: config = tomli.load(fp)

def test_make_dataset_from_toml():
    """
    test_make_dataset_from_toml
    
    Tests that the number of simulated results matches the number expected based on the prescribed toml file.
    See [Documentation/Usage](https://pediatriciqphantoms.readthedocs.io/en/latest/usage.html#examples) for more details on setting up config toml files
    """
    testdir = Path(config['simulation'][0]['image_directory'])

    if testdir.exists(): rmtree(testdir)

    run(['make_phantoms', config_file])

    simulation_results = list(testdir.rglob('*.mhd'))

    nphantoms = len(config['simulation'][0]['model'])
    ndiameters = len(config['simulation'][0]['diameter'])
    ndose_levels = len(config['simulation'][0]['dose_level'])

    assert(len(simulation_results) == nphantoms*ndiameters*(ndose_levels+1)) # a ground truth file is added which is like another dose level