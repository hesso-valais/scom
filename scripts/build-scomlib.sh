#!/usr/bin/env bash

SCRIPT_DIR=${0%/*}
WORK_DIR=${SCRIPT_DIR}/../src/sino/scom

# Be sure virtual environment is set up
cd ${SCRIPT_DIR}/..
pipenv install

# Start build in the 'root' folder
cd ${SCRIPT_DIR}/..

# Remove generated files to force a complete build
rm -f ${WORK_DIR}/*.cpp
rm -f ${WORK_DIR}/*.pyd
rm -f ${WORK_DIR}/*.so

# Build the extension
pipenv run python ./src/sino/scom/setup.py build_ext --inplace

# Move it to right location 'eq.: sino/scom'
mv -f baseframe.*so ${WORK_DIR}/
mv -f property.*so ${WORK_DIR}/
