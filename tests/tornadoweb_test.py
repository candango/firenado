#!/usr/bin/env python
#
# Copyright 2015-2021 Flavio Garcia
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

import firenado.conf
from firenado.tornadoweb import get_request, TornadoApplication, TornadoHandler
from firenado.launcher import FirenadoLauncher, TornadoLauncher
from firenado.tornadoweb import TornadoComponent
import unittest
from tests import chdir_app
import os


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
        chdir_app("tornadoweb")
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


class GetRequestTestCase(unittest.TestCase):

    def test_get_request_simple(self):
        expected = "http://test"
        request = get_request(expected)
        self.assertEqual(expected, request.url)
        self.assertEqual(0, len(request.headers))
        self.assertEqual("GET", request.method)

    def test_get_request_with_path(self):
        expected = "http://test/a_path/informed"
        base_url = "http://test"
        request = get_request(url=base_url, path="a_path/informed")
        self.assertEqual(expected, request.url)
        base_url = "http://test/"
        request = get_request(url=base_url, path="a_path/informed")
        self.assertEqual(expected, request.url)

    def test_get_request_with_method(self):
        method = "POST"
        request = get_request(url="http://test", method=method)
        self.assertEqual(method, request.method)

    def test_get_request_with_form_urlencoded(self):
        request = get_request(url="http://test", form_urlencoded=True)
        self.assertEqual(1, len(request.headers))
        self.assertEqual("application/x-www-form-urlencoded",
                         request.headers['Content-Type'])


class TornadoHandlerTestCase(unittest.TestCase):
    """ TornadoHandler tests
    """

    def setUp(self):
        """ Application configuration file will be read and components will be
        loaded.
        """
        chdir_app("tornadoweb")
        self.application = TornadoApplication()

    def test_authenticated(self):
        kwargs = {"component": self.application.components['test']}
        handler = MainHandler(self.application, FakeRequest(), **kwargs)
        self.assertFalse(handler.authenticated())
        handler.current_user = "a user"
        self.assertTrue(handler.authenticated())


class TornadoLaucherTestCase(unittest.TestCase):
    """ TornadoLaucher tests
    """

    def test_parameters_none(self):
        """ Test if launcher parameters will be none if not informed
        """
        launcher = FirenadoLauncher()
        self.assertIsNone(launcher.addresses)
        self.assertIsNone(launcher.dir)
        self.assertIsNone(launcher.port)

    def test_parameters_addresses_and_port(self):
        """ Test if launcher parameters were set correctly if informed
        addresses, dir and port
        """
        addresses = "localhost"
        dir = os.path.dirname(os.path.abspath(__file__))
        port = 80
        launcher = FirenadoLauncher(addresses=addresses, dir=dir, port=port)
        self.assertEqual(addresses, launcher.addresses)
        self.assertEqual(dir, launcher.dir)
        self.assertEqual(port, launcher.port)

    def test_parameters_socket(self):
        """ Test if launcher parameters were set correctly if informed dir and
        socket
        """
        dir = os.path.dirname(os.path.abspath(__file__))
        socket = "/tmp/a_socket_file"
        launcher = FirenadoLauncher(dir=dir, socket=socket)
        self.assertEqual(dir, launcher.dir)
        self.assertEqual(socket, launcher.socket)

    def test_load(self):
        chdir_app("tornadoweb")
        launcher = TornadoLauncher()
        launcher.load()
        self.assertTrue(isinstance(launcher.application, TornadoApplication))
