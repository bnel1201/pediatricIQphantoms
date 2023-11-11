# %%
# https://realpython.com/python-toml/
# %%
import tomli
import os
with open("test.toml", mode="rb") as fp:
    config = tomli.load(fp)
config
# %%
interpretor = 'matlab -r'
cmd = f"""
{interpretor} "basedir='{os.path.abspath(config['directories']['image_directory'])}';\
    resultsdir='{os.path.abspath(config['directories']['results_directory'])}';\
    run('evaluation/NPS/main_nps_catphanSim.m');exit"
"""
os.system(cmd)
# %%
