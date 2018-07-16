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

import firenado.conf
from firenado.tornadoweb import TornadoApplication
from firenado.tornadoweb import TornadoHandler
from firenado.tornadoweb import TornadoComponent
import unittest
from tests import chdir_app


class MainHandler(TornadoHandler):
    """ Basic handler rendering an index.html template
    """

    def get(self):
        self.render("index.html", initial_message="Hello world!!!")


class TestComponent(TornadoComponent):
    """ Enabled component referenced at the application configuration file
    """

    def get_handlers(self):
        return [
            (r'/', MainHandler),
        ]


class FakeRequest:

    def __init__(self):
        self.connection = FakeConnection()


class FakeConnection:

    def set_close_callback(self, callback):
        pass

class DisabledTestComponent(TornadoComponent):
    """ Disabled component referenced at the application configuration file
    """

    def get_handlers(self):
        return [
            (r'/', MainHandler),
        ]


class ApplicationComponentTestCase(unittest.TestCase):
    """ Case that tests an Firenado application after being loaded from its
    configuration file.
    """

    def setUp(self):
        """ Application configuration file will be read and components will be
        loaded.
        """
        chdir_app('tornadoweb')
        self.application = TornadoApplication()

    def test_component_loaded(self):
        """ Checks if test component was loaded correctly by the application
        __init__ method.
        """
        import tests.tornadoweb_test
        self.assertTrue('test' in self.application.components)
        self.assertTrue(isinstance(self.application.components['test'],
                                   tests.tornadoweb_test.TestComponent))
        self.assertFalse('disabled' in self.application.components)

    def test_static_path(self):
        """ Checks the static_path was placed in the application settings.
        """
        static_path_x = self.application.settings['static_path'].split("/")
        self.assertEqual(firenado.conf.app['static_path'], static_path_x[-1])


class TornadoHandlerTestCase(unittest.TestCase):
    """ TornadoHandler tests
    """

    def setUp(self):
        """ Application configuration file will be read and components will be
        loaded.
        """
        chdir_app('tornadoweb')
        self.application = TornadoApplication()

    def test_authenticated(self):
        kwargs = {"component": self.application.components['test']}
        handler = MainHandler(self.application, FakeRequest(), **kwargs)
        self.assertFalse(handler.authenticated())
        handler.current_user = "a user"
        self.assertTrue(handler.authenticated())
