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
	../dtop/pyenv/bin/black . --exclude="fastbar|archive"
	../dtop/pyenv/bin/isort .
