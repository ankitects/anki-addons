all: clean
	(cd japanese && zip -r ../japanese.zip *)
	zip chinese.zip chinese.py unihan.db

clean:
	rm -f japanese.zip chinese.zip *.pyc japanese/*.pyc japanese/__pycache__

