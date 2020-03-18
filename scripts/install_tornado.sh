#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.

PYTHON_VERSION=`python -c 'import sys; print(sys.version_info[0])'`

if [ $PYTHON_VERSION -eq 2 ]; then
    pip install -r requirements/tornado_legacy.txt;
    exit;
else:
    pip install -r requirements/tornado_new.txt;
    exit;
fi
exit 0;
