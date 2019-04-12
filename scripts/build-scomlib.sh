#!/usr/bin/env bash

WORK_DIR=${0%/*}

# Be sure virtual environment is set up
cd ${WORK_DIR}/..
#pipenv install

# Start build in the 'src' folder
cd ${WORK_DIR}/../src

# Remove generated files to force a complete build
rm -f sino/scom/*.cpp
rm -f sino/scom/*.pyd
rm -f sino/scom/*.so

pipenv run python ./sino/scom/setup.py build_ext --inplace
