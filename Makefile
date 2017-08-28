ZIP=zip -r --exclude=meta.json

all: prepare zips/japanese.zip zips/quickcolours.zip zips/cardstats.zip zips/print.zip

zips/japanese.zip: $(shell find japanese -type f | grep -v pycache)
	(cd japanese && $(ZIP) ../zips/japanese.zip *)

zips/quickcolours.zip: quickcolours/__init__.py
	(cd quickcolours && $(ZIP) ../zips/quickcolours.zip *)	

zips/cardstats.zip: cardstats/__init__.py
	(cd cardstats && $(ZIP) ../zips/cardstats.zip *)	

zips/print.zip: print/__init__.py
	(cd print && $(ZIP) ../zips/print.zip *)	

prepare:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	test -d zips || mkdir zips

clean:
	rm -rf zips
