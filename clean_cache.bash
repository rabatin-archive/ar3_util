#!/bin/bash
# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################

if [ -f "setup.py" ]; then
    echo "About to remove various cache paths"
else
    echo "Must be called from the directory where setup.py is located"
    echo "Exiting"
    exit 1
fi

CNT=`find . -name '__pycache__' | wc -l`
echo "Found $CNT cache paths(s)"

find . -name '__pycache__' -exec 'rm' '-rf' '{}' ';' 2>/dev/null

echo "Done"