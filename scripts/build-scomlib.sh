#!/usr/bin/env bash

WORK_DIR=${0%/*}

# Start build where 'src' folder is located
cd ${WORK_DIR}/..

pipenv run python ./src/sino/scom/setup.py build_ext --inplace
