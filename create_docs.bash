#!/bin/bash
# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################

if [ -f "docs/conf.py" ]; then
    echo "About to rebuild documentation"
else
    echo "Must be called from the directory where docs is located"
    echo "Exiting"
    exit 1
fi

source version_info.bash

set_version_info

rm -rf docs/ar3_util.rst
rm -rf docs/modules.rst
rm -rf docs/_build
sphinx-apidoc -o docs ar3_util
cd docs
make html

remove_version_info
