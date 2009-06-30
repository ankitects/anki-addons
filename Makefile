all: clean
	zip -r japanese.zip jp.py japanese
	zip chinese.zip chinese.py unihan.db

clean:
	rm -f japanese.zip chinese.zip *.pyc japanese/*.pyc

