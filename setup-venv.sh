#!/bin/bash

set -e

cd ../anki
./tools/python -m venv ~/Local/python/addons
~/Local/python/addons/bin/pip install black isort mypy pylint mock types-mock
