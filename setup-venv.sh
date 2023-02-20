#!/bin/bash

set -e

python3 -m venv ~/Local/python/addons
~/Local/python/addons/bin/pip install black isort mypy pylint mock types-mock
