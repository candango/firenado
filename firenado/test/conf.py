#!/usr/bin/env python
#
# Copyright 2015-2017 Flavio Garcia
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


class ApplicationComponentTestCase(unittest.TestCase):
    """ Case that tests an Firenado application after being loaded from its
    configuration file.
    """

    def test_conf_root(self):
        """ Test if Firenado root matches the upper directory relative to the
        current one. """
        import os
        current_path = os.path.dirname(os.path.realpath(__file__))
        firenado_root = ("%s" % os.sep).join(current_path.split(os.sep)[:-1])
        self.assertEqual(firenado_root, firenado.conf.ROOT)

    def test_conf_root(self):
        """ Test if Firenado root matches the upper directory relative to the
        current one. """
        current_path = os.path.dirname(os.path.realpath(__file__))
        firenado_root = ("%s" % os.sep).join(current_path.split(os.sep)[:-1])
        self.assertEqual(firenado_root, firenado.conf.ROOT)

    def test_firenado_config_file_default_value(self):
        """ Test if the default Firenado config file value will be "firenado".
        """
        self.assertEqual("firenado", firenado.conf.FIRENADO_CONFIG_FILE)

    def test_firenado_config_file_custom_value(self):
        """ Test if Firenado config file value will be changed setting
        FIRENADO_CONFIG_FILE env variable.
        """
        custom_file_name = "custom_file"
        os.environ['FIRENADO_CONFIG_FILE'] = custom_file_name
        reload(firenado.conf)
        self.assertEqual(firenado.conf.FIRENADO_CONFIG_FILE, custom_file_name)
        del os.environ['FIRENADO_CONFIG_FILE']
        reload(firenado.conf)

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
        chdir_app("yml", "conf")
        self.assertEquals(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)
        self.assertEquals(firenado.conf.stack[1],
                          firenado.conf.APP_CONFIG_FILE)

    def test_app_port(self):
        """ Checks if the app port is set correctly.
        """
        # Loading file from test/resources/session/file/conf/firenado.yml
        chdir_app("file", "session")
        self.assertTrue(firenado.conf.app['socket'] is None)
        self.assertEquals(firenado.conf.app['port'], 8887)

    def test_app_pythonpath(self):
        """ Checks if the pythonpath is set on the application config file.
        """
        chdir_app("file", "session")
        self.assertEquals(firenado.conf.app['pythonpath'], "..")

    def test_yml_loaded(self):
        """ On an application with a yml and yaml config files the yml should
        be loaded.
        """
        chdir_app("yml", "conf")
        self.assertEquals("yml", _file.get_file_extension(
                firenado.conf.APP_CONFIG_FILE))

    def test_static_path(self):
        """ If static path is defined on the app configuration.
        """
        chdir_app("yml", "conf")
        self.assertEquals("yml_static_path", firenado.conf.app['static_path'])

    def test_root_url(self):
        """ Test if the root path was set on the app configuration.
        """
        chdir_app("root_url", "conf")
        self.assertEquals("a_root_url", firenado.conf.app['url_root_path'])

    def test_root_url_slash_in_front(self):
        """ Test if the root path with a slash in the front will be returned
        without it was set on the app configuration.
        """
        chdir_app("root_url_slash_in_front", "conf")
        self.assertEquals("a_root_url",  firenado.conf.app['url_root_path'])

    def test_root_url_slash_none(self):
        """ Test if the root path with a slash in the front will be returned
        without it was set on the app configuration.
        """
        chdir_app("root_url_slash_none", "conf")
        self.assertEquals(None,  firenado.conf.app['url_root_path'])

    def test_static_path(self):
        """ If static url prefix is defined on the app configuration.
        """
        chdir_app("yml", "conf")
        self.assertEquals("yml_static_url_prefix",
                          firenado.conf.app['static_url_prefix'])

    def test_session_type_file(self):
        """ Checks if the session is enabled and the type is file
        """
        chdir_app("file", "session")
        self.assertEquals(firenado.conf.session['enabled'], True)
        self.assertEquals(firenado.conf.session['type'], "file")

    def test_session_name_default(self):
        """ Checks if the session name is default, FIRENADOSESSID
        """
        chdir_app("file", "session")
        self.assertEquals(firenado.conf.session['enabled'], True)
        self.assertEquals(firenado.conf.session['name'], "FIRENADOSESSID")

    def test_session_type_redis(self):
        """ Checks if the session is enabled and the type is redis
        """
        chdir_app("redis", "session")
        self.assertEquals(firenado.conf.session['enabled'], True)
        self.assertEquals(firenado.conf.session['type'], "redis")

    def test_session_name_custom(self):
        """ Checks if the session name will be defined as in the config file
        """
        chdir_app("redis", "session")
        self.assertEquals(firenado.conf.session['enabled'], True)
        self.assertEquals(firenado.conf.session['name'], "REDISSESSID")


class MultiAppTestCase(unittest.TestCase):
    """ Case that tests multi app configuration.
    """

    def test_multi_app_true(self):
        """ Checks if the application is multi app
        """
        chdir_app("multiapp")
        self.assertTrue(firenado.conf.app['multi'])

    def test_multi_app_false(self):
        """ Checks if the application isn't multi app
        """
        chdir_app("tornadoweb")
        self.assertFalse(firenado.conf.app['multi'])
