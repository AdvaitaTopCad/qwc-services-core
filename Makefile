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
	$(RMRF) dist || echo "dist not found, skipping"
	$(RMRF) build || echo "build not found, skipping"
	$(RMRF) $(MODULE_NAME).egg-info || echo "egg-info not found, skipping"
	python -m build
	python -m twine check dist/*

lint:
	@python -m isort --check $(MODULE_NAME)  ||  echo "isort:   FAILED!"
	@python -m black --check --quiet $(MODULE_NAME)  || echo "black:   FAILED!"
	@python -m flake8 $(MODULE_NAME)  || echo "flake8:  FAILED!"

delint:
	python -m isort $(MODULE_NAME)
	python -m black $(MODULE_NAME)

typecheck:
	python -m mypy $(MODULE_NAME)

test: lint typecheck
	python -m pytest \
		--cov-report term \
		--cov-report html \
		--cov-config=.coveragerc \
		--cov=$(MODULE_NAME) $(MODULE_NAME)/

# https://packaging.python.org/guides/using-testpypi
testdist: sdist
	python -m twine upload --repository testpypi dist/*
	echo Test with `python -m pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)`

publish: sdist
	python -m twine upload dist/*
