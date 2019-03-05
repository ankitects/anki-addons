#!/bin/bash

modules=$(find . -name __init__.py -maxdepth 2 | perl -pe 's%./(.+)/__init__.py%\1%')
PYTHONPATH=../dtop pylint -j 0 --rcfile=../dtop/.pylintrc -f colorized --extension-pkg-whitelist=PyQt5 $modules

