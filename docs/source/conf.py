# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pediatricIQphantoms'
copyright = '2024, Brandon Nelson, Rongping Zeng'
author = 'Brandon Nelson, Rongping Zeng'
release = '0.0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


# sys.path.insert(0, pathlib.Path(__file__).parents[2]/'src/pediatricIQphantoms')
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.duration',
              'sphinx.ext.doctest',
              'sphinx.ext.autosummary',
              'sphinx_tabs.tabs',
              'sphinxcontrib.inkscapeconverter']
 #https://docs.readthedocs.io/en/stable/guides/jupyter.html

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
# html_static_path = ['_static']
