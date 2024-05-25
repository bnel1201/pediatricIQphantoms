from pathlib import Path
from shutil import rmtree
import tomli
from subprocess import run

test_dir = Path(__file__).parent.absolute()
config_file = test_dir / 'configs/test.toml'

with open(config_file, mode="rb") as fp: config = tomli.load(fp)

def test_make_dataset_from_toml():
    """
    test_make_dataset_from_toml
    
    Tests that the number of simulated results matches the number expected based on the prescribed toml file.
    See [Documentation/Usage](https://pediatriciqphantoms.readthedocs.io/en/latest/usage.html#examples) for more details on setting up config toml files
    """
    results_dir = Path(config['simulation'][0]['image_directory'])

    if results_dir.exists(): rmtree(results_dir)

    run(['make_phantoms', config_file])

    simulation_results = list(results_dir.rglob('*.dcm'))

    nphantoms = len(config['simulation'][0]['model'])
    ndiameters = len(config['simulation'][0]['diameter'])
    nsims = config['simulation'][0]['nsims']
    ndose_levels = len(config['simulation'][0]['dose_level']) + 1 # a ground truth file is added which is like another dose level

    assert(len(simulation_results) == nphantoms*ndiameters*ndose_levels*nsims) 