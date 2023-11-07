MODULE_NAME = qwc_services_core
PACKAGE_NAME = qwc-services-core
ifeq ($(OS),Windows_NT)
    detected_OS := Windows
else
    detected_OS := $(shell uname)
endif
ifeq ($(OS),Windows_NT) 
	RMRF = rmdir /s /q
else
	RMRF = rm -rf
endif

all: lint test testdist

sdist:
	$(RMRF) dist
	$(RMRF) build
	python setup.py sdist bdist_wheel
	python -m twine check dist/*

lint:
	@python -m isort --check $(MODULE_NAME)  ||  echo "isort:   FAILED!"
	@python -m black --check --quiet $(MODULE_NAME)  || echo "black:   FAILED!"

delint:
	python -m isort $(MODULE_NAME)
	python -m black $(MODULE_NAME)

typecheck:
	python -m mypy $(MODULE_NAME)

test:
	python -m pytest -v

testdist: sdist
	# https://packaging.python.org/guides/using-testpypi
	python -m twine upload --repository testpypi dist/*
	echo Test with `python -m pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)`

publish: sdist
	python -m twine upload dist/*
