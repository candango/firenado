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

from __future__ import (absolute_import, division, print_function,
                        with_statement)

from firenado.core import TornadoApplication, TornadoHandler, TornadoComponent
import unittest
import firenado.conf
import firenado.util.file as _file
import six
import os

if six.PY3:
    if six.PY34:
        import importlib
        reload = importlib.reload
    else:
        import imp
        reload = imp.reload


def chdir_app(app_name):
    """ Change to the application directory located at the resource directory
    for conf tests.

    The conf resources directory is firenado/firenado/test/resources/conf.

    :param app_name: The application name
    """
    test_dirname, filename = os.path.split(os.path.abspath(__file__))
    test_app_dirname = os.path.join(test_dirname, 'resources',
                                          'conf', app_name)
    os.chdir(test_app_dirname)
    reload(firenado.conf)


class ApplicationComponentTestCase(unittest.TestCase):
    """ Case that tests an Firenado application after being loaded from its
    configuration file.
    """

    def test_only_framework_stack(self):
        """ Tests is only the framework config stack was loaded.
        No app config is provided.
        """
        self.assertEquals(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)

    def test_app_stack(self):
        """ Application config is provided. Test if the app config file was
        loaded.
        """
        chdir_app('yml')
        self.assertEquals(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)
        self.assertEquals(firenado.conf.stack[1],
                          firenado.conf.APP_CONFIG_FILE)

    def test_yml_loaded(self):
        """ On an application with a yml and yaml config files the yml should
        be loaded.
        """
        chdir_app('yml')
        self.assertEquals('yml', _file.get_file_extension(
                firenado.conf.APP_CONFIG_FILE))

    def test_static_path(self):
        """ If static path is defined than app configuration should get it.
        """
        chdir_app('yml')
        self.assertEquals('yml_static_path', firenado.conf.app['static_path'])

