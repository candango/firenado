# Copyright 2015-2023 Flavio Garcia
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

from firenado.data import DataConnectedMixin
from firenado.service import with_service, FirenadoService
import unittest


class TestableServiceDataConnected(FirenadoService):
    """ Serves a data connected method directly.
    When decorating a data connected directly the service must return the
    consumer.
    """
    pass


class TestableSession(object):

    def __init__(self, data_source):
        self._data_source = data_source
        self._oppened = True

    @property
    def data_source(self):
        return self._data_source

    @property
    def is_oppened(self):
        return self._oppened

    @property
    def name(self):
        return self.data_source.resolve_session()

    def close(self):
        self._oppened = False


class TestableDataSource(object):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def session(self):
        return TestableSession(self)

    @property
    def session_resolved_string(self):
        return "Session resolved from data source"

    def resolve_session(self):
        return "%s: %s" % (self.session_resolved_string, self.name)


class TestableDataConnected(DataConnectedMixin):
    """ Data connected mock object. This object holds the data sources to be
    used in the test cases.
    """

    testable_service_data_connected: TestableServiceDataConnected

    def __init__(self):
        self.data_sources['datasource1'] = TestableDataSource("DataSource1")
        self.data_sources['datasource2'] = TestableDataSource("DataSource2")

    @with_service(TestableServiceDataConnected)
    def get_service_data_sources_directly(self):
        return self.testable_service_data_connected.get_data_sources()


class TestableService(FirenadoService):
    """ Service that decorates the instance to be served directly and
    indirectly thought MockTestServiceRecursion.
    When decorating directly data connected and data sources will be returned
    in one interaction.
    When decorating indirectly MockTestServiceRecursion will be used to return
    the data connected instance and data sources.
    """
    pass


class RecursiveService(FirenadoService):
    """ This service will be used to return the data connected reference
    and data source, during the recursive test, delegating to MockTestService.
    """

    testable_service: TestableService

    @with_service(TestableService)
    def get_service_data_sources_recursively(self):
        return self.testable_service.get_data_sources()

    @with_service(TestableService)
    def get_data_connected_recursively(self):
        return self.testable_service.data_connected


class ServedByInstance(object):
    """ Class with methods to be decorated with the served_by decorator.
    """

    testable_service: TestableService
    recursive_service: RecursiveService

    def __init__(self, data_connected):
        self.data_connected = data_connected

    @with_service(TestableService)
    def do_served_by_class(self):
        """ Method to be decorated with served_by with a class reference
        """
        pass

    @with_service("tests.service_test.TestableService")
    def do_served_by_string(self):
        """ Method to be decorated with served_by with a string as class
        reference
        """
        pass

    @with_service(TestableService)
    def get_service_data_connected(self):
        return self.testable_service.data_connected

    @with_service(RecursiveService)
    def get_service_data_connected_recursively(self):
        return (self.recursive_service.get_data_connected_recursively())

    @with_service(TestableService)
    def get_service_data_sources(self):
        """ This method returns the data sources from the data connected
        instance of this class. The method is returned by the service defined
        on the served_by decorator. Here there is no recursion once
        MockTestService is directly serving the ServiceByInstance.
        """
        return self.testable_service.get_data_sources()

    @with_service(RecursiveService)
    def get_service_data_sources_recursively(self):
        """ Same as get_service_data_sources but service will be serving
        another service defined here and then access the data sources
        """
        return (self.recursive_service.get_service_data_sources_recursively())

    def get_data_connected(self):
        return self.data_connected


class ServiceTestCase(unittest.TestCase):

    def setUp(self):
        """ Setting up an object that has firenado.core.service.served_by
        decorators on some methods.
        """
        self.data_connected_instance = TestableDataConnected()
        self.served_by_instance = ServedByInstance(
            self.data_connected_instance)

    def test_served_by_class_reference(self):
        self.assertFalse(hasattr(self.served_by_instance, 'testable_service'))
        self.served_by_instance.do_served_by_class()
        self.assertTrue(hasattr(self.served_by_instance, 'testable_service'))
        self.assertTrue(isinstance(
            self.served_by_instance.testable_service, TestableService))

    def test_served_by_class_name_string(self):
        self.assertFalse(hasattr(self.served_by_instance, 'testable_service'))
        self.served_by_instance.do_served_by_string()
        self.assertTrue(hasattr(self.served_by_instance, 'testable_service'))
        self.assertEqual(
            self.served_by_instance.testable_service.__class__.__name__,
            TestableService.__name__)

    def test_data_connected_from_service(self):
        data_connected = self.served_by_instance.get_data_connected()
        self.assertEqual(data_connected, self.data_connected_instance)

    def test_data_connected_from_service_recursively(self):
        data_connected = (self.served_by_instance.
                          get_service_data_connected_recursively())
        self.assertEqual(data_connected, self.data_connected_instance)

    def test_data_connected_from_service_none(self):
        service = TestableService(None)
        data_connected = service.data_connected
        self.assertIsNone(data_connected)

    def test_get_data_source_from_service(self):
        data_sources = self.served_by_instance.get_service_data_sources()
        self.assertTrue(len(data_sources) == 2)
        self.assertEqual(data_sources['datasource1'].name, "DataSource1")
        self.assertEqual(data_sources['datasource2'].name, "DataSource2")

    def test_get_data_source_from_data_connected(self):
        data_sources = (self.data_connected_instance.
                        get_service_data_sources_directly())
        self.assertTrue(len(data_sources) == 2)
        self.assertEqual(data_sources['datasource1'].name, "DataSource1")
        self.assertEqual(data_sources['datasource2'].name, "DataSource2")

    def test_get_data_source_from_service_recursively(self):
        data_sources = (self.served_by_instance.
                        get_service_data_sources_recursively())
        self.assertTrue(len(data_sources) == 2)
        self.assertEqual(data_sources['datasource1'].name, "DataSource1")
        self.assertEqual(data_sources['datasource2'].name, "DataSource2")

    def test_get_data_source_from_service_none(self):
        service = TestableService(None)
        data_sources = service.get_data_sources()
        self.assertIsNone(data_sources)
