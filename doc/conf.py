import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Elevating Efficiency'
html_title = 'Elevating Efficiency Documentation'
copyright = '2023, Brian Funk, Andrin Gasser and Silvan Metzker'
author = 'Brian Funk, Andrin Gasser and Silvan Metzker'

sys.path.insert(0, os.path.abspath('..'))
autodoc_mock_imports = ['hard_to_install_module', 'module_with_c_extensions']


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'main.py']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
