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

import importlib
import yaml
import os
import logging

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

# Application file
APP_ROOT_PATH = os.path.join(os.getcwd())
# If FIRENADO_CURRENT_APP_PATH is not set than return current directory
# conf dir
APP_CONFIG_PATH = os.getenv('FIRENADO_CURRENT_APP_CONFIG_PATH',
                            os.path.join(APP_ROOT_PATH, 'conf'))
APP_CONFIG_FILE = os.path.join(APP_CONFIG_PATH, FIRENADO_CONFIG_FILE)

HAS_LIB_CONFIG_FILE = False
HAS_APP_CONFIG_FILE = False

if os.path.isfile(LIB_CONFIG_FILE):
    HAS_LIB_CONFIG_FILE = True
    stack.append(LIB_CONFIG_FILE)

if os.path.isfile(APP_CONFIG_FILE):
    if APP_CONFIG_FILE != LIB_CONFIG_FILE:
        HAS_APP_CONFIG_FILE = True
        stack.append(APP_CONFIG_FILE)

# Tmp path variable
# TODO: Should I care about windows?
TMP_SYS_PATH = '/tmp'
TMP_APP_PATH = TMP_SYS_PATH

# Setting firenado's default variables

# Application section
app = {}
# Key to to be used on on the session context to store and retrieve the current
# logged user
app['component'] = None
app['current_user_key'] = '__FIRENADO_CURRENT_USER_KEY__'
app['data'] = {}
app['data']['sources'] = []
app['pythonpath'] = None
app['port'] = 8888
app['login'] = {}
app['login']['urls'] = {}
app['login']['urls']['default'] = '/login'
app['is_on_dir'] = False

# Component section
components = {}

# Data section
data = {}
data['connectors'] = {}
data['sources'] = {}

# Logging default configuration
log = {}
log['format'] = None
log['level'] = logging.NOTSET

# Management section
management = {}
management['commands'] = {}

# Session section
session = {}
session['enabled'] = False
session['encoder'] = 'pickle'
session['encoders'] = {}
session['file'] = {}
session['file']['path'] = ''
session['handlers'] = {}
session['name'] = 'FIRENADOSESSID'
session['redis'] = {}
session['redis']['data'] = {}
session['redis']['data']['source'] = ''
session['redis']['prefix'] = 'firenado:session'
session['type'] = ''


def log_level_from_string(str_level):
    """ Returns the proper log level core based on a given string
    """
    levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }
    try:
        return levels[str_level.upper()]
    except KeyError:
        pass
    except AttributeError:
        if str_level in [logging.DEBUG, logging.INFO, logging.WARNING,
                         logging.ERROR, logging.CRITICAL]:
            return str_level
    return logging.NOTSET


def get_class_from_config(config):
    """ Returns a class from a config dict bit with the keys
    module and class on it. 
    """
    module = importlib.import_module(config['module'])
    return getattr(module, config['class'])


def load_yaml_config_file(path):
    """ Returns the parsed structure from a yaml config file.
    """
    return yaml.safe_load(file(path, 'r'))


def process_config(config):
    """ Populates firenado.conf attributes from the loaded configuration
    dict. It handles data and management aspects from the configuration.

    :param config: Loaded configuration dict
    """
    if 'components' in config:
        process_components_config_section(config['components'])
    if 'data' in config:
        process_data_config_section(config['data'])
    if 'log' in config:
        process_log_config_section(config['log'])
    if 'management' in config:
        process_management_config_section(config['management'])
    if 'session' in config:
        process_session_config_section(config['session'])


def process_app_config(config):
    """ Populates firenado.conf attributes from the loaded configuration
    dict. It handles everything that process_config does plus application
    configuation.

    :param config: Loaded configuration dict
    """
    process_config(config)
    if 'app' in config:
        process_app_config_section(config['app'])


def process_app_config_section(app_config):
    """ Processes the app section from a configuration dict.

    :param app_config: App section from a config dict
    data.
    """
    global app
    if 'component' in app_config:
        app['component'] = app_config['component']
    if 'data' in app_config:
        if 'sources' in app_config['data']:
            app['data']['sources'] = app_config['data']['sources']
    if 'pythonpath' in app_config:
        app['pythonpath'] = app_config['pythonpath']
    if 'port' in app_config:
        app['port'] = app_config['port']


def process_components_config_section(components_config):
    """ Processes the components section from a configuration dict.

    :param components_config: Data section from a config dict.
    """
    global components
    for component_config in components_config:
        if 'id' not in component_config:
            raise Exception('The component %s was defined without an id.' %
                            component_config)
        component_id = component_config['id']
        if component_id not in components:
            components[component_id] = {}
            components[component_id]['enabled'] = False
            components[component_id]['config'] = {}
        if 'class' in component_config:
            class_config_x = component_config['class'].split('.')
            components[component_id]['class'] = class_config_x[-1]
            components[component_id]['module'] = '.'.join(class_config_x[:-1])
        if 'enabled' in component_config:
            components[component_id]['enabled'] = bool(
                component_config['enabled'])


def process_data_config_section(data_config):
    """ Processes the data configuration section from the configuration
    dict.

    :param data_config: Data configuration section from a config dict.
    """
    global data
    if 'connectors' in data_config:
        for connector in data_config['connectors']:
            connector_class_x = connector['class'].split('.')
            connector['class'] = connector_class_x[-1]
            connector['module'] = '.'.join(connector_class_x[:-1][:])
            data['connectors'][connector['name']] = connector
            del data['connectors'][connector['name']]['name']
    if 'sources' in data_config:
        for source in data_config['sources']:
            data['sources'][source['name']] = source
            del data['sources'][source['name']]['name']


def process_log_config_section(log_config):
    """ Processes the log section from a configuration dict.

    :param log_config: Log section from a config dict.
    """
    global log
    if 'format' in log_config:
        log['format'] = log_config['format']
    if 'level' in log_config:
        log['level'] = log_config['level']


def process_management_config_section(management_config):
    """ Processes the management section from a configuration dict.

    :param management_config: Management section from a config dict.
    """
    global management
    if 'commands' in management_config:
        management['commands'] = management_config['commands']


def process_session_config_section(session_config):
    """ Processes the session section from the configuration dict.

    :param session_config: Session configuration section from a config dict.
    """
    global session
    if 'enabled' in session_config:
        session['enabled'] = session_config['enabled']
    if 'type' in session_config:
        session['type'] = session_config['type']
        if session['type'] == 'file':
            if 'path' in session_config:
                session['file']['path'] = session_config['path']
        if session['type'] == 'redis':
            if 'data' in session_config:
                if 'source' in session_config['data']:
                    session['redis']['data']['source'] = session_config[
                        'data']['source']
    if 'handlers' in session_config:
        for handler in session_config['handlers']:
            handler_class_x = handler['class'].split('.')
            handler['class'] = handler_class_x[-1]
            handler['module'] = '.'.join(handler_class_x[:-1][:])
            session['handlers'][handler['name']] = handler
            del session['handlers'][handler['name']]['name']
    if 'encoders' in session_config:
        for encoder in session_config['encoders']:
            encoder_class_x = encoder['class'].split('.')
            encoder['encoder'] = encoder_class_x[-1]
            encoder['class'] = encoder_class_x[-1]
            encoder['module'] = '.'.join(encoder_class_x[:-1][:])
            session['encoders'][encoder['name']] = encoder
            del session['encoders'][encoder['name']]['name']

if HAS_LIB_CONFIG_FILE:
    lib_config = load_yaml_config_file(LIB_CONFIG_FILE)
    process_config(lib_config)

if HAS_APP_CONFIG_FILE:
    app_config = load_yaml_config_file(APP_CONFIG_FILE)
    process_app_config(app_config)

# Set logging basic configurations
logging.basicConfig(level=log_level_from_string(log['level']),
                    format=log['format'])
