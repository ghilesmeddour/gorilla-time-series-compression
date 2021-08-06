TESTS_DIR=tests

format:
	yapf -irp .

dead-code-check:
	vulture src --min-confidence 70

test:
	python -m unittest discover ${TESTS_DIR}

type-check:
	mypy src --ignore-missing-imports

coverage:
	coverage run --source=src -m unittest discover ${TESTS_DIR}
	coverage report -m
	coverage html

build:
	rm -rf dist
	python -m pip install --upgrade build
	python -m build
	twine check dist/*

push:
	twine upload dist/*
