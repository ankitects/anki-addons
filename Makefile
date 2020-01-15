all: prepare buildall

prepare:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete

buildall:
	test -d _build || mkdir _build
	python3 build.py

clean:
	rm -rf _build

fix:
	../dtop/pyenv/bin/black code
	../dtop/pyenv/bin/isort code

check:
	../dtop/pyenv/bin/mypy code
	../dtop/pyenv/bin/pylint -j 0 --rcfile=../dtop/pylib/.pylintrc -f colorized \
	--extension-pkg-whitelist=ankirspy,PyQt5 code/*
