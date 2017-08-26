all: prepare zips/japanese.zip zips/quickcolours.zip zips/cardstats.zip

zips/japanese.zip: $(shell find japanese -type f)
	(cd japanese && zip -r ../zips/japanese.zip *)

zips/quickcolours.zip: quickcolours/__init__.py
	(cd quickcolours && zip -r ../zips/quickcolours.zip *)	

zips/cardstats.zip: cardstats/__init__.py
	(cd cardstats && zip -r ../zips/cardstats.zip *)	

prepare:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	test -d zips || mkdir zips

clean:
	rm -rf zips
