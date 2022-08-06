# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################

import os
from setuptools import setup

ar3_version = os.getenv('__AR3__BUILD_VERSION__')
ar3_author = os.getenv('__AR3__BUILD_AUTHOR__')

setup(
  name='ar3_util',
  version=ar3_version,
  packages=['ar3_util'],
  url='www.rabatin.com',
  license='MIT',
  author=ar3_author,
  author_email='arthur@rabatin.com',
  description='Collection of Utlities'
)
