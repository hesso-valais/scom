#!/usr/bin/env bash

WORK_DIR=${0%/*}

# Start build in the 'scom' folder
cd ${WORK_DIR}/..

pipenv run python setup.py sdist
