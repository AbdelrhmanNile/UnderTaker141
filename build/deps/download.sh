#!/bin/bash
set -x
################################################################################
# File:    build/deps/download.sh
# Purpose: Use this script to download the files in this dir. Useful if, for
#          example, you don't trust their integrity and/or want to verify them.
#
#          * https://github.com/BusKill/buskill-app/issues/2
#
# Note:    This script was built to be run in Debian or TAILS
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-08-19
# Updated: 2020-08-19
# Version: 0.1
################################################################################

sudo apt-get -y install python3-pip python3-setuptools

CURL="/usr/bin/curl"
WGET="/usr/bin/wget --retry-on-host-error --retry-connrefused"
PYTHON="/usr/bin/python3"

tmpDir=`mktemp -d`
pushd "${tmpDir}"

# first get some info about our internet connection
${CURL} -s https://ifconfig.co/country | head -n1
${CURL} -s https://check.torproject.org | grep Congratulations | head -n1

# and today's date
date -u +"%Y-%m-%d"

# first download and upgrade pip (required to get some wheels)
${PYTHON} -m pip download --no-cache-dir pip
${PYTHON} -m pip install --upgrade pip


# misc linux
${WGET} --output-document=python.AppImage https://github.com/niess/python-appimage/releases/download/python3.11/python3.11.9-cp311-cp311-manylinux2014_x86_64.AppImage
${WGET} https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
${WGET} --output-document=squashfs4.4.tar.gz https://sourceforge.net/projects/squashfs/files/squashfs/squashfs4.4/squashfs4.4.tar.gz/download


