MAKEFLAGS += -j

all: build

venv:
	test -d ~/Local/python/addons || ./setup-venv.sh
	~/Local/python/addons/bin/pip install --pre aqt[qt6]

check: check_format mypy pylint

check_format: venv
	~/Local/python/addons/bin/black --exclude=vendor/ --check code demos
	~/Local/python/addons/bin/isort --check code demos

mypy: venv
	~/Local/python/addons/bin/mypy code demos

pylint: venv
	~/Local/python/addons/bin/pylint -j 10 -f colorized \
	--extension-pkg-whitelist=PyQt6 code/* demos/*

fix:
	~/Local/python/addons/bin/black --exclude=vendor/ code demos
	~/Local/python/addons/bin/isort code demos

build: check
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	(cd code && ~/Local/python/addons/bin/python ../build.py)
	open ~/.cache/anki-addons &
