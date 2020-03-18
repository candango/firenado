#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.

PYTHON_VERSION=`python -c 'import sys; print(sys.version_info[0])'`

if [ $PYTHON_VERSION -eq 2 ]; then
    pip install tornado==5.1.1;
    exit;
fi
exit 0;
