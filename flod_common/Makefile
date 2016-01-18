all: lint test

lint:
	find . -name '*.py' -exec flake8 --max-complexity=5 {} +

clean:
	find . -name '*.pyc' -exec rm -f {} +

test:
	nosetests
