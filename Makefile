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
	~/Local/py514/bin/black --exclude=vendor/ code demos
	~/Local/py514/bin/isort code demos

check:
	~/Local/py514/bin/mypy code demos
	~/Local/py514/bin/pylint -j 0 --rcfile=../dtop/pylib/.pylintrc -f colorized \
	--extension-pkg-whitelist=ankirspy,PyQt5 code/* demos/*
