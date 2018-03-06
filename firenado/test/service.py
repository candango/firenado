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

from firenado.data import DataConnectedMixin
from firenado.service import served_by, FirenadoService


class MockDataConnected(DataConnectedMixin):
    """ Data connected mock object. This object holds the data sources to be
    used in the test cases.
    """

    def __init__(self):
        self.data_sources['datasource1'] = 'DataSource1'
        self.data_sources['datasource2'] = 'DataSource2'


class MockTestService(FirenadoService):
    """ Service that decorates the instance to be served directly and
    indirectly thought MockTestServiceRecursion.
    When decorating directly data connected and data sources will be returned
    in one interaction.
    When decorating indirectly MockTestServiceRecursion will be used to return
    the data connected instance and data sources.
    """
    pass


class MockTestServiceRecursion(FirenadoService):
    """ Service that decorates the instance to be served and will be used
    to return the data connected and data sources when MockTestService
    delegates to during the recursive test.
    """

    @served_by(MockTestService)
    def get_service_data_sources_recursively(self):
        return self.mock_test_service.get_data_sources()

    @served_by(MockTestService)
    def get_data_connected_recursively(self):
        return self.mock_test_service.data_connected


class ServedByInstance(object):
    """ Class that has methods that will be decorated with the served_by
    decorator.
    """

    def __init__(self, data_connected):
        self.data_connected = data_connected

    @served_by(MockTestService)
    def do_served_by_class(self):
        """
        This method will be decorated with served_by with the class reference
        """
        pass

    @served_by('firenado.test.service.MockTestService')
    def do_served_by_string(self):
        """
        This method will be decorated with served_by with the class as string
        """
        pass

    @served_by(MockTestService)
    def get_service_data_connected(self):
        return self.mock_test_service.data_connected

    @served_by(MockTestServiceRecursion)
    def get_service_data_connected_recursively(self):
        return self.mock_test_service_recursion.\
            get_data_connected_recursively()

    @served_by(MockTestService)
    def get_service_data_sources(self):
        """ This method returns the data sources from the data connected
        instance of this class. The method is returned by the service defined
        on the served_by decorator. Here there is no recursion once
        MockTestService is directly serving the ServiceByInstance.
        """
        return self.mock_test_service.get_data_sources()

    @served_by(MockTestServiceRecursion)
    def get_service_data_sources_recursively(self):
        """ Same as get_service_data_sources but the a service will be serving
        the service defined here and then access the data sources
        """
        return self.mock_test_service_recursion.\
            get_service_data_sources_recursively()

    def get_data_connected(self):
        return self.data_connected


class ServiceTestCase(unittest.TestCase):

    def setUp(self):
        """ Setting up an object that has firenado.core.service.served_by
        decorators on some methods.
        """
        self.data_connected_instance = MockDataConnected()
        self.served_by_instance = ServedByInstance(
            self.data_connected_instance)

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

    def test_data_connected_from_service(self):
        data_connected = self.served_by_instance.get_data_connected()
        self.assertEquals(data_connected, self.data_connected_instance)

    def test_data_connected_from_service_recursively(self):
        data_connected = self.served_by_instance.\
            get_service_data_connected_recursively()
        self.assertEquals(data_connected, self.data_connected_instance)

    def test_data_connected_from_service_none(self):
        mock_service = MockTestService(None)
        data_connected = mock_service.data_connected
        self.assertIsNone(data_connected)

    def test_get_data_source_from_service(self):
        data_sources = self.served_by_instance.get_service_data_sources()
        self.assertTrue(len(data_sources) == 2)
        self.assertEquals(data_sources['datasource1'], "DataSource1")
        self.assertEquals(data_sources['datasource2'], "DataSource2")

    def test_get_data_source_from_service_recursively(self):
        data_sources = self.served_by_instance.\
            get_service_data_sources_recursively()
        self.assertTrue(len(data_sources) == 2)
        self.assertEquals(data_sources['datasource1'], "DataSource1")
        self.assertEquals(data_sources['datasource2'], "DataSource2")

    def test_get_data_source_from_service_none(self):
        mock_service = MockTestService(None)
        data_sources = mock_service.get_data_sources()
        self.assertIsNone(data_sources)
