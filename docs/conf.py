# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################

from pathlib import Path

# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


ar3_version = os.getenv('__AR3__BUILD_VERSION__')
ar3_author = os.getenv('__AR3__BUILD_AUTHOR__')


# -- Project information -----------------------------------------------------
project = 'AR3 Util'
copyright = '2022, Arthur Rabatin'
author = ar3_version
release = ar3_author

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
