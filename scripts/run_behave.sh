#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.

PYTHON_VERSION=`python -c 'import sys; print(sys.version_info[0])'`

if [ $PYTHON_VERSION -eq 3 ]; then
    behave tests/features; 
    exit;
fi
exit 0;
