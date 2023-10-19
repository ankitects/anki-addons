#!/bin/bash
#
# Updates venv to use locally-built wheels, for changes that haven't made it into
# a PyPi update.

set -e

(cd ../anki && ./ninja wheels)
~/Local/python/addons/bin/pip install --upgrade ../anki/out/wheels/*
