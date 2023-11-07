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

all: test testdist

sdist:
	$(RMRF) dist
	$(RMRF) build
	python setup.py sdist bdist_wheel
	python -m twine check dist/*

test:
	python -m pytest -v

testdist: sdist
	# https://packaging.python.org/guides/using-testpypi
	python -m twine upload --repository testpypi dist/*
	echo Test with `python -m pip install --index-url https://test.pypi.org/simple/ qwc-services-core`

publish: sdist
	python -m twine upload dist/*
