#!/bin/bash
set -x
################################################################################
# File:    linux/buildAppImage.sh
# Purpose: Builds a self-contained AppImage executable for a simple Hello World
#          GUI app using kivy. See also:
#
#          * https://kivy.org/doc/stable/installation/installation-linux.html
#          * https://kivy.org/doc/stable/guide/basic.html
#          * https://github.com/AppImage/AppImageKit/wiki/Bundling-Python-apps
#
# Authors: Michael Altfield <michael@buskill.in>
# Created: 2020-05-30
# Updated: 2020-05-31
# Version: 0.2
################################################################################

############
# SETTINGS #
############

PYTHON_PATH='/usr/bin/python3.11'

###################
# INSTALL DEPENDS #
###################

# install os-level depends
sudo apt-get update; sudo apt-get -y install python3.11 python3-pip python3-setuptools wget rsync fuse
sudo apt install --only-upgrade libglib2.0-0
sudo apt reinstall libxmlb2


uname -a
cat /etc/issue
which python
which python3.11
ldconfig -p | grep libglib
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH



# setup a virtualenv to isolate our app's python depends
#${PYTHON_PATH} -m pip install --upgrade --user pip setuptools
#${PYTHON_PATH} -m pip install --upgrade --user virtualenv
#${PYTHON_PATH} -m virtualenv /tmp/kivy_venv

# install kivy and all other python dependencies with pip into our virtual env
# we'll later add these to our AppDir for building the AppImage
#source /tmp/kivy_venv/bin/activate; python -m pip install -r requirements.txt

##################
# PREPARE APPDIR #
##################

# cleanup old appdir, if exists
rm -rf /tmp/kivy_appdir

# We use this python-appimage release as a base for building our own python
# AppImage. We only have to add our code and depends to it.
cp build/deps/python3.11.4-cp311-cp311-manylinux2014_x86_64.AppImage /tmp/python.AppImage
chmod +x /tmp/python.AppImage
/tmp/python.AppImage --appimage-extract
mv squashfs-root /tmp/kivy_appdir

# copy depends that were installed with kivy into our kivy AppDir
#rsync -a /tmp/kivy_venv/ /tmp/kivy_appdir/opt/python3.11/
#/tmp/kivy_appdir/opt/python3.11/bin/python3.11 -m pip install -r requirements.txt
/tmp/kivy_appdir/AppRun -m pip install -r requirements.txt

# add our code to the AppDir
rsync -a src /tmp/kivy_appdir/opt/

# rm the default icon
rm /tmp/kivy_appdir/usr/share/icons/hicolor/256x256/apps/python.png
# copy our icon to the AppDir
rsync -a undertaker.png /tmp/kivy_appdir/usr/share/icons/hicolor/256x256/apps/python.png

#delete the default desktop file
rm /tmp/kivy_appdir/usr/share/applications/python3.11.4.desktop
# copy our desktop file to the AppDir
rsync -a build/UnderTaker141.desktop /tmp/kivy_appdir/usr/share/applications/python3.11.4.desktop

cat /tmp/kivy_appdir/usr/share/metainfo/python3.11.4.appdata.xml


# change AppRun so it executes our app
mv /tmp/kivy_appdir/AppRun /tmp/kivy_appdir/AppRun.orig
cat > /tmp/kivy_appdir/AppRun <<'EOF'
#! /bin/bash

# Export APPRUN if running from an extracted image
self="$(readlink -f -- $0)"
here="${self%/*}"
APPDIR="${APPDIR:-${here}}"

# Export TCl/Tk
export TCL_LIBRARY="${APPDIR}/usr/share/tcltk/tcl8.5"
export TK_LIBRARY="${APPDIR}/usr/share/tcltk/tk8.5"
export TKPATH="${TK_LIBRARY}"

# Export SSL certificates
export SSL_CERT_FILE="${APPDIR}/opt/_internal/certs.pem"

# Call the entry point
for opt in "$@"
do
    [ "${opt:0:1}" != "-" ] && break
    if [[ "${opt}" =~ "I" ]] || [[ "${opt}" =~ "E" ]]; then
        # Environment variables are disabled ($PYTHONHOME). Let's run in a safe
        # mode from the raw Python binary inside the AppImage
        "$APPDIR/opt/python3.11/bin/python3.11 $APPDIR/opt/src/app.py" "$@"
        exit "$?"
    fi
done

# Get the executable name, i.e. the AppImage or the python binary if running from an
# extracted image
executable="${APPDIR}/opt/python3.11/bin/python3.11 ${APPDIR}/opt/src/app.py"
if [[ "${ARGV0}" =~ "/" ]]; then
    executable="$(cd $(dirname ${ARGV0}) && pwd)/$(basename ${ARGV0})"
elif [[ "${ARGV0}" != "" ]]; then
    executable=$(which "${ARGV0}")
fi

# Wrap the call to Python in order to mimic a call from the source
# executable ($ARGV0), but potentially located outside of the Python
# install ($PYTHONHOME)
(PYTHONHOME="${APPDIR}/opt/python3.11" exec -a "${executable}" "$APPDIR/opt/python3.11/bin/python3.11" "$APPDIR/opt/src/app.py" "$@")
exit "$?"
EOF

# make it executable
chmod +x /tmp/kivy_appdir/AppRun

##################
# BUILD APPIMAGE #
##################

# create the AppImage from kivy AppDir
cp build/deps/appimagetool-x86_64.AppImage /tmp/appimagetool.AppImage
chmod +x /tmp/appimagetool.AppImage

# create the dist dir for our result to be uploaded as an artifact
# note tha gitlab will only accept artifacts that are in the build dir (cwd)
mkdir dist
/tmp/appimagetool.AppImage /tmp/kivy_appdir dist/UnderTaker141.AppImage

#######################
# OUTPUT VERSION INFO #
#######################

uname -a
cat /etc/issue
which python
python --version
python -m pip list

##################
# CLEANUP & EXIT #
##################

# exit cleanly
exit 0
