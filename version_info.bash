#!/bin/bash
# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################


# IMPORTANT
# ------------------------------------------------------------------------------------------
# This is the auhoritative version information used anywhere in build tools for this project
# Do no define any release information elsewhere
# This is meant to be sourced from various build scripts
RELEASE_VERSION='0.5'
RELEASE_AUTHOR='Arthur Rabatin'

function set_version_info {
  export __AR3__BUILD_VERSION__=$RELEASE_VERSION
  export __AR3__BUILD_AUTHOR__=$RELEASE_AUTHOR
}

function remove_version_info {
  unset __AR3__BUILD_VERSION__
  unset __AR3__BUILD_AUTHOR__
}

