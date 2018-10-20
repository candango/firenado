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

import unittest
import firenado.conf
import firenado.util.file as _file
from tests import chdir_app
import logging
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
        firenado_root = os.path.join(firenado_root, "firenado")
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

    def test_system_config_path_default_value(self):
        """ Test if the default system config path is /etc/firenado
        """
        self.assertEqual(firenado.conf.SYS_CONFIG_PATH, "/etc/firenado")

    def test_system_config_path_custom_value(self):
        """ Test if the default system config path will be changed setting the
        FIRENADO_SYS_CONFIG_PATH env variable
        """
        custom_sys_config_path = "/etc/anotherplace"
        os.environ['FIRENADO_SYS_CONFIG_PATH'] = custom_sys_config_path
        reload(firenado.conf)
        self.assertEqual(firenado.conf.SYS_CONFIG_PATH, custom_sys_config_path)
        del os.environ['FIRENADO_SYS_CONFIG_PATH']
        reload(firenado.conf)

    def test_only_framework_stack(self):
        """ Tests is only the framework config stack was loaded.
        No app config is provided.
        """
        self.assertEqual(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)

    def test_app_stack(self):
        """ Application config is provided. Test if the app config file was
        loaded.
        """
        chdir_app("yml", "conf")
        self.assertEqual(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)
        self.assertEqual(firenado.conf.stack[1],
                          firenado.conf.APP_CONFIG_FILE)

    def test_sys_stack(self):
        """ System config path is provided. Test if the system config file was
        loaded.
        """
        os.environ['FIRENADO_SYS_CONFIG_PATH'] = os.path.join(
            os.path.dirname(__file__), "resources", "conf", "sys_config")
        reload(firenado.conf)
        self.assertEqual(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)
        self.assertEqual(firenado.conf.stack[1],
                          firenado.conf.SYS_CONFIG_FILE)
        self.assertEqual("sys_log_format", firenado.conf.log['format'])
        self.assertEqual(logging.DEBUG, firenado.conf.log['level'])
        del os.environ['FIRENADO_SYS_CONFIG_PATH']
        reload(firenado.conf)

    def test_app_addresses_default(self):
        """ If no addresses are provided to the application we default to
        ipv4 and ipv6 loopbacks.
        """
        # There is no addresses configured into the conf/yml firenado.yml
        chdir_app("yml", "conf")
        self.assertTrue(firenado.conf.app['socket'] is None)
        self.assertEqual(len(firenado.conf.app['addresses']), 2)
        self.assertEqual(firenado.conf.app['addresses'][0], "::")
        self.assertEqual(firenado.conf.app['addresses'][1], "0.0.0.0")

    def test_app_addresses_from_conf(self):
        """ Getting localhost defined into the configuration.
        """
        # At the conf/root_url app.addresses has only localhost
        chdir_app("root_url", "conf")
        self.assertTrue(firenado.conf.app['socket'] is None)
        self.assertEqual(len(firenado.conf.app['addresses']), 1)
        self.assertEqual(firenado.conf.app['addresses'][0], "localhost")

    def test_app_port(self):
        """ Checks if the app port is set correctly.
        """
        # Loading file from test/resources/session/file/conf/firenado.yml
        chdir_app("file", "session")
        self.assertTrue(firenado.conf.app['socket'] is None)
        self.assertEqual(firenado.conf.app['port'], 8887)

    def test_app_pythonpath(self):
        """ Checks if the pythonpath is set on the application config file.
        """
        chdir_app("file", "session")
        self.assertEqual(firenado.conf.app['pythonpath'], "..")

    def test_yml_loaded(self):
        """ On an application with a yml and yaml config files the yml should
        be loaded.
        """
        chdir_app("yml", "conf")
        self.assertEqual("yml", _file.get_file_extension(
                firenado.conf.APP_CONFIG_FILE))

    def test_static_path(self):
        """ If static path is defined on the app configuration.
        """
        chdir_app("yml", "conf")
        self.assertEqual("yml_static_path", firenado.conf.app['static_path'])

    def test_root_url(self):
        """ Test if the root path was set on the app configuration.
        """
        chdir_app("root_url", "conf")
        self.assertEqual("a_root_url", firenado.conf.app['url_root_path'])

    def test_root_url_slash_in_front(self):
        """ Test if the root path with a slash in the front will be returned
        without it was set on the app configuration.
        """
        chdir_app("root_url_slash_in_front", "conf")
        self.assertEqual("a_root_url",  firenado.conf.app['url_root_path'])

    def test_root_url_slash_none(self):
        """ Test if the root path with a slash in the front will be returned
        without it was set on the app configuration.
        """
        chdir_app("root_url_slash_none", "conf")
        self.assertEqual(None,  firenado.conf.app['url_root_path'])

    def test_static_path(self):
        """ If static url prefix is defined on the app configuration.
        """
        chdir_app("yml", "conf")
        self.assertEqual("yml_static_url_prefix",
                          firenado.conf.app['static_url_prefix'])

    def test_session_type_file(self):
        """ Checks if the session is enabled and the type is file
        """
        chdir_app("file", "session")
        self.assertEqual(firenado.conf.session['enabled'], True)
        self.assertEqual(firenado.conf.session['type'], "file")

    def test_session_name_default(self):
        """ Checks if the session name is default, FIRENADOSESSID
        """
        chdir_app("file", "session")
        self.assertEqual(firenado.conf.session['enabled'], True)
        self.assertEqual(firenado.conf.session['name'], "FIRENADOSESSID")

    def test_session_type_redis(self):
        """ Checks if the session is enabled and the type is redis
        """
        chdir_app("redis", "session")
        self.assertEqual(firenado.conf.session['enabled'], True)
        self.assertEqual(firenado.conf.session['type'], "redis")

    def test_session_name_custom(self):
        """ Checks if the session name will be defined as in the config file
        """
        chdir_app("redis", "session")
        self.assertEqual(firenado.conf.session['enabled'], True)
        self.assertEqual(firenado.conf.session['name'], "REDISSESSID")


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
