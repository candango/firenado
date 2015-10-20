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

from firenado.core.service import served_by, FirenadoService
import unittest


class MockTestService(FirenadoService):
    pass


class ServedByInstance:
    """ Class that has methods that will be decorated with the served_by
    decorator.
    """

    @served_by(MockTestService)
    def do_served_by_class(self):
        """
        This method will be decorated with served_by with the class reference
        """
        pass

    @served_by('firenado.test.core.service.MockTestService')
    def do_served_by_string(self):
        """
        This method will be decorated with served_by with the class as string
        """
        pass


class ApplicationComponentTestCase(unittest.TestCase):

    def setUp(self):
        """ Setting up an object that has firenado.core.service.served_by
        decorators on some methods.
        """
        self.served_by_instance = ServedByInstance()

    def test_served_by_class_reference(self):
        self.assertFalse(hasattr(self.served_by_instance, 'mock_test_service'))
        self.served_by_instance.do_served_by_class()
        self.assertTrue(hasattr(self.served_by_instance, 'mock_test_service'))
        self.assertTrue(isinstance(
            self.served_by_instance.mock_test_service, MockTestService))

    def test_served_by_class_name_string(self):
        self.assertFalse(hasattr(self.served_by_instance, 'mock_test_service'))
        self.served_by_instance.do_served_by_string()
        self.assertTrue(hasattr(self.served_by_instance, 'mock_test_service'))
        self.assertEqual(
            self.served_by_instance.mock_test_service.__class__.__name__,
            MockTestService.__name__)
