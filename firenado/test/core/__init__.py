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

import os
test_dirname, filename = os.path.split(os.path.abspath(__file__))
test_resources_dirname = os.path.join(test_dirname, '..', 'resources', 'core')
os.environ["FIRENADO_CURRENT_APP_CONFIG_PATH"] = \
    os.path.join(test_resources_dirname, 'conf')

from firenado.core import TornadoApplication, TornadoHandler, TornadoComponent
import unittest


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
        self.application = TornadoApplication()

    def test_component_loaded(self):
        """ Checks if test component was loaded correctly by the application
        __init__ method.
        """
        self.assertTrue('test' in self.application.components)
        self.assertTrue(isinstance(self.application.components['test'],
                                   TestComponent))
        self.assertFalse('disabled' in self.application.components)
