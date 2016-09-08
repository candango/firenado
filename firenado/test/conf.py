#!/usr/bin/env python
#
# Copyright 2015-2016 Flavio Garcia
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

import unittest
import firenado.conf
import firenado.util.file as _file
from firenado.test import chdir_app


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
        chdir_app('yml', 'conf')
        self.assertEquals(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)
        self.assertEquals(firenado.conf.stack[1],
                          firenado.conf.APP_CONFIG_FILE)

    def test_app_port(self):
        """ Checks if the app port is set correctly.
        """
        # Loading file from test/resources/session/file/conf/firenado.yml
        chdir_app('file', 'session')
        self.assertTrue(firenado.conf.app['socket'] is None)
        self.assertEquals(firenado.conf.app['port'], 8887)

    def test_app_pythonpath(self):
        chdir_app('file', 'session')
        self.assertEquals(firenado.conf.app['pythonpath'], "..")

    def test_yml_loaded(self):
        """ On an application with a yml and yaml config files the yml should
        be loaded.
        """
        chdir_app('yml', 'conf')
        self.assertEquals('yml', _file.get_file_extension(
                firenado.conf.APP_CONFIG_FILE))

    def test_static_path(self):
        """ If static path is defined than app configuration should get it.
        """
        chdir_app('yml', 'conf')
        self.assertEquals('yml_static_path', firenado.conf.app['static_path'])

    def test_session_type_file(self):
        """ Checks if the session is enabled and the type is file
        """
        chdir_app('file', 'session')
        self.assertEquals(firenado.conf.session['enabled'], True)
        self.assertEquals(firenado.conf.session['type'], "file")


    def test_session_type_redis(self):
        """ Checks if the session is enabled and the type is redis
        """
        chdir_app('redis', 'session')
        self.assertEquals(firenado.conf.session['enabled'], True)
        self.assertEquals(firenado.conf.session['type'], 'redis')