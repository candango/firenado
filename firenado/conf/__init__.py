#!/usr/bin/env python
#
# Copyright 2015-2018 Flavio Garcia
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

from __future__ import (absolute_import, division, print_function,
                        with_statement)

import firenado.config as _config
import logging
import os
import sys

# Setting root path
ROOT = None
if os.path.abspath(__file__).endswith('.py') or \
        os.path.abspath(__file__).endswith('.pyc'):
    ROOT = os.path.dirname(os.path.abspath(__file__))
else:
    ROOT = os.path.abspath(__file__)
ROOT = os.path.abspath(os.path.join(ROOT, '..'))

# Getting configuration paths and files from the environment
FIRENADO_CONFIG_FILE = None
try:
    FIRENADO_CONFIG_FILE = os.environ['FIRENADO_CONFIG_FILE']
except KeyError:
    FIRENADO_CONFIG_FILE = 'firenado'

stack = []

LIB_CONFIG_FILE = os.path.join(ROOT, 'conf', FIRENADO_CONFIG_FILE)

# Application file
APP_ROOT_PATH = os.path.join(os.getcwd())
# If FIRENADO_CURRENT_APP_CONFIG_PATH is not set than return current directory
# conf dir
APP_CONFIG_PATH = os.getenv('FIRENADO_CURRENT_APP_CONFIG_PATH',
                            os.path.join(APP_ROOT_PATH, 'conf'))
#print(APP_CONFIG_PATH)
APP_CONFIG_FILE = os.path.join(APP_CONFIG_PATH, FIRENADO_CONFIG_FILE)

# If FIRENADO_SYS_CONFIG_PATH is not set than set default sys config path
SYS_CONFIG_PATH = os.getenv('FIRENADO_SYS_CONFIG_PATH',
                            os.path.join(os.sep, "etc", "firenado"))
SYS_CONFIG_FILE = os.path.join(SYS_CONFIG_PATH, FIRENADO_CONFIG_FILE)

HAS_LIB_CONFIG_FILE = False
HAS_SYS_CONFIG_FILE = False
HAS_APP_CONFIG_FILE = False

config_file_extensions = ['yml', 'yaml']
for extension in config_file_extensions:
    if not HAS_LIB_CONFIG_FILE:
        if os.path.isfile('%s.%s' % (LIB_CONFIG_FILE, extension)):
            HAS_LIB_CONFIG_FILE = True
            LIB_CONFIG_FILE = '%s.%s' % (LIB_CONFIG_FILE, extension)
            stack.append(LIB_CONFIG_FILE)
    if not HAS_SYS_CONFIG_FILE:
        if os.path.isfile('%s.%s' % (SYS_CONFIG_FILE, extension)):
            HAS_SYS_CONFIG_FILE = True
            SYS_CONFIG_FILE = '%s.%s' % (SYS_CONFIG_FILE, extension)
            stack.append(SYS_CONFIG_FILE)
    if not HAS_APP_CONFIG_FILE:
        if os.path.isfile('%s.%s' % (APP_CONFIG_FILE, extension)):
            HAS_APP_CONFIG_FILE = True
            APP_CONFIG_FILE = '%s.%s' % (APP_CONFIG_FILE, extension)
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
app['addresses'] = ["::", "0.0.0.0"]
app['component'] = None
app['cookie_secret'] = None
app['current_user_key'] = "__FIRENADO_CURRENT_USER_KEY__"
app['data'] = {}
app['data']['sources'] = []
app['debug'] = False
app['id'] = None
app['pythonpath'] = None
app['port'] = 8888
app['login'] = {}
app['login']['urls'] = {}
app['login']['urls']['default'] = "/login"
app['multi'] = False
app['is_on_dir'] = False
app['session'] = {
    'id_generator': "default",
}
app['settings'] = {}
app['socket'] = None
app['static_path'] = None
app['static_url_prefix'] = "/static"
app['type'] = "tornado"
app['types'] = {}
app['types']['tornado'] = {}
app['types']['tornado']['name'] = "tornado"
app['types']['tornado']['launcher'] = {}
app['types']['tornado']['launcher']['class'] = "TornadoLauncher"
app['types']['tornado']['launcher']['module'] = "firenado.tornadoweb"
app['url_root_path'] = None
# Wait before shutdown is on seconds
app['wait_before_shutdown'] = 0
app['xsrf_cookies'] = False

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
management['commands'] = []

# Session section
session = {}
# Default session hiccup time is 10 seconds
# This is the time the callback will hiccup if purge_limit is reached
session['callback_hiccup'] = 10
# Default session callback time is 2 minutes
# This is the time the application will scan for expired sessions
session['callback_time'] = 120
session['enabled'] = False
session['encoder'] = 'pickle'
session['encoders'] = {}
session['file'] = {}
session['file']['path'] = ''
session['handlers'] = {}
session['id_generators'] = {}
# Default session life time is 30 minutes or 1800 seconds
# If set to 0 the session will not expire
session['life_time'] = 1800
session['name'] = 'FIRENADOSESSID'
session['purge_limit'] = 500
session['redis'] = {}
session['redis']['data'] = {}
session['redis']['data']['source'] = ''
session['redis']['prefix'] = 'firenado:session'
session['type'] = ''

if HAS_LIB_CONFIG_FILE:
    lib_config = _config.load_yaml_config_file(LIB_CONFIG_FILE)
    _config.process_config(sys.modules[__name__], lib_config)

if HAS_SYS_CONFIG_FILE:
    sys_config = _config.load_yaml_config_file(SYS_CONFIG_FILE)
    _config.process_config(sys.modules[__name__], sys_config)

if HAS_APP_CONFIG_FILE:
    app_config = _config.load_yaml_config_file(APP_CONFIG_FILE)
    _config.process_app_config(sys.modules[__name__], app_config)

# Set logging basic configurations
logging.basicConfig(level=log['level'], format=log['format'])
