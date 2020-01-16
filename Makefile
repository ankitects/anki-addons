all: buildall

prepare:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete

buildall: check prepare
	test -d build || mkdir build
	(cd code && python3 ../build.py)

clean:
	rm -rf build

fix:
	../dtop/pyenv/bin/black code demos
	../dtop/pyenv/bin/isort code demos

check:
	../dtop/pyenv/bin/mypy code demos
	../dtop/pyenv/bin/pylint -j 0 --rcfile=../dtop/pylib/.pylintrc -f colorized \
	--extension-pkg-whitelist=ankirspy,PyQt5 code/* demos/*
