#!/usr/bin/env python
#
# Copyright 2015 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:

from __future__ import (absolute_import, division,
                        print_function, with_statement)
import yaml
import os

# Setting root path
ROOT = None
if os.path.abspath(__file__).endswith('.py') or \
        os.path.abspath(__file__).endswith('.pyc'):
    ROOT = os.path.dirname(os.path.abspath(__file__))
else:
    ROOT = os.path.abspath(__file__)

# Getting configuration paths and files from the environment
FIRENADO_CONFIG_FILE = None
try:
    FIRENADO_CONFIG_FILE = os.environ['FIRENADO_CONFIG_FILE']
except KeyError:
    FIRENADO_CONFIG_FILE = 'firenado.yaml'

stack = []

LIB_CONFIG_FILE = os.path.join(ROOT, 'conf', FIRENADO_CONFIG_FILE)

HAS_LIB_CONFIG_FILE = False

if os.path.isfile(LIB_CONFIG_FILE):
    HAS_LIB_CONFIG_FILE = True
    stack.append(LIB_CONFIG_FILE)

# Data default configuration
data = dict()
data['connectors'] = dict()

# Management default configuration
management = dict()
management['commands'] = dict()

def process_config(config):
    """ Processes a configuration loaded from a config file populating
    the module data.
    :param config: Configuration loaded from a config file
    """
    if 'data' in config:
        process_data_config(config['data'])


def process_data_config(data_config):
    """ Processes the data configuration section loaded from a config file.
    :param data_config: Data configuration section from a configuration loaded
    from a file.
    """
    global data
    if 'connectors' in data_config:
        data['connectors'] = data_config['connectors']


if HAS_LIB_CONFIG_FILE:
    lib_config = yaml.safe_load(file(LIB_CONFIG_FILE, 'r'))
    process_config(lib_config)
