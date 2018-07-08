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

import os
import six

if six.PY3:
    try:
        import importlib
        reload = importlib.reload
    except AttributeError:
        # PY33
        import imp
        reload = imp.reload


def chdir_app(app_name, dir_name=None):
    """ Change to the application directory located at the resource directory
    for conf tests.

    The conf resources directory is firenado/tests/resources/conf.

    :param app_name: The application name
    """
    import firenado.conf

    test_dirname, filename = os.path.split(os.path.abspath(__file__))
    if dir_name:
        test_app_dirname = os.path.join(test_dirname, 'resources',
                                        dir_name, app_name)
    else:
        test_app_dirname = os.path.join(test_dirname, 'resources', app_name)
    os.chdir(test_app_dirname)
    reload(firenado.conf)
