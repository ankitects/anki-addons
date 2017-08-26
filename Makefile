all: nocache japanese.zip quickcolours.zip cardstats.zip

japanese.zip: $(shell find japanese -type f)
	(cd japanese && zip -r ../japanese.zip *)

quickcolours.zip: quickcolours/__init__.py
	(cd quickcolours && zip -r ../quickcolours.zip *)	

cardstats.zip: cardstats/__init__.py
	(cd cardstats && zip -r ../cardstats.zip *)	

nocache:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete

clean:
	rm -rf *.zip
