# Development

[Home](../README.md)

This section contains information for developers. In case you want to improve, debug, 
extend the project you may find here some useful information.

## Useful Commands

Manually build extension modules:
```bash
$ pipenv run setup.py build_ext --inplace
```
After build, you need to manually copy them into the `src/sino/scom/` folder.

Install package needed for deployment (coverage, build, twine, etc.):
```bash
$ pipenv install --dev
```

## Running Test Coverage
To run the test coverage execute the following commands:
```bash
$ pipenv run coverage run --source=./src -m unittest discover -s tests/sino
$ pipenv run coverage report -m
```
