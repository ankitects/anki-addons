#!/bin/bash

set -e

python3 -m venv ~/Local/python/addons
~/Local/python/addons/bin/pip install -r requirements-dev.txt
