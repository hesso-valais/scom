#!/usr/bin/env bash

WORK_DIR=${0%/*}

# Start build in the 'src' folder
cd ${WORK_DIR}/../src

pipenv run python ./sino/scom/setup.py build_ext --inplace
