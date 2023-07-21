lint:
	. ./venv/bin/activate && pylint ./src/*.py

test:
	. ./venv/bin/activate && cd tests && pytest

all: lint test
