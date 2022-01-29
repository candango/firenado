#!/usr/bin/env python
#
# Copyright 2015-2022 Flávio Gonçalves Garcia
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
from firenado.service import served_by, sessionned, FirenadoService
import unittest


class MockServiceDataConnected(FirenadoService):
    """ Serves a data connected method directly.
    When decorating a data connected directly the service must return the
    consumer.
    """
    pass


class MockSession(object):

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


class MockDataSource(object):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def session(self):
        return MockSession(self)

    @property
    def session_resolved_string(self):
        return "Session resolved from data source"

    def resolve_session(self):
        return "%s: %s" % (self.session_resolved_string, self.name)


class MockDataConnected(DataConnectedMixin):
    """ Data connected mock object. This object holds the data sources to be
    used in the test cases.
    """

    def __init__(self):
        self.data_sources['datasource1'] = MockDataSource("DataSource1")
        self.data_sources['datasource2'] = MockDataSource("DataSource2")

    @served_by(MockServiceDataConnected)
    def get_service_data_sources_directly(self):
        return self.mock_service_data_connected.get_data_sources()


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


class MockSessionedService(FirenadoService):

    @sessionned
    def resolve_from_default_data_source(self, **kwargs):
        return kwargs

    @sessionned(data_source="datasource1")
    def resolve_from_data_source(self, **kwargs):
        return kwargs

    @property
    def default_data_source(self):
        return "datasource2"


class ServedByInstance(object):
    """ Class with methods to be decorated with the served_by decorator.
    """

    def __init__(self, data_connected):
        self.data_connected = data_connected

    @served_by(MockTestService)
    def do_served_by_class(self):
        """ Method to be decorated with served_by with a class reference
        """
        pass

    @served_by('tests.service_test.MockTestService')
    def do_served_by_string(self):
        """ Method to be decorated with served_by with a string as class
        reference
        """
        pass

    @served_by(MockTestService)
    def get_service_data_connected(self):
        return self.mock_test_service.data_connected

    @served_by(MockTestServiceRecursion)
    def get_service_data_connected_recursively(self):
        return (self.mock_test_service_recursion.
                get_data_connected_recursively())

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
        return (self.mock_test_service_recursion.
                get_service_data_sources_recursively())

    def get_data_connected(self):
        return self.data_connected


class SessionedTestCase(unittest.TestCase):

    mock_sessioned_service: MockSessionedService

    def setUp(self):
        """ Setting up an object that has firenado.core.service.served_by
        decorators on some methods.
        """
        self.data_connected_instance = MockDataConnected()
        self.served_by_instance = ServedByInstance(
            self.data_connected_instance)

    @property
    def data_connected(self):
        return self.served_by_instance.data_connected

    @served_by(MockSessionedService)
    def test_sessioned_default_data_source(self):
        """ Method resolve_from_default_data_source is anoteded with sessioned
        and no parameter. The data source to be used is the one defined either
        in the property or method named default_data_source. In this case we're
        using a property.
        """
        resolved_kwargs = (
            self.mock_sessioned_service.resolve_from_default_data_source()
        )
        print(resolved_kwargs)
        self.assertEqual("datasource2", resolved_kwargs['data_source'])
        data_source = self.data_connected.get_data_source(
            resolved_kwargs['data_source']
        )
        self.assertEqual(data_source.resolve_session(),
                         resolved_kwargs['session'].name)
        self.assertTrue(resolved_kwargs['session'].is_oppened)

    @served_by(MockSessionedService)
    def test_sessioned_default_data_source_my_session(self):
        """ Method resolve_from_default_data_source is anoteded with sessioned
        and no parameter. Instead of getting the session from the default data
        source, we're providing our own session.
        """
        data_source = self.data_connected.get_data_source("datasource1")
        resolved_kwargs = (
            self.mock_sessioned_service.resolve_from_default_data_source(
                session=data_source.session
            )
        )
        # No datasource will be added to the kwards
        self.assertIsNone(resolved_kwargs.get("data_source"))
        # Using session provided
        self.assertEqual(data_source.resolve_session(),
                         resolved_kwargs['session'].name)
        self.assertTrue(resolved_kwargs['session'].is_oppened)

    @served_by(MockSessionedService)
    def test_sessioned_from_data_source(self):
        """ Method resolve_from_data_source is anoteded with sessioned and
        datasource1 as parameter. It will be injected to the method kwargs
        session from datasource1.
        """
        resolved_kwargs = (
            self.mock_sessioned_service.resolve_from_data_source()
        )
        self.assertEqual("datasource1", resolved_kwargs['data_source'])
        data_source = self.data_connected.get_data_source(
            resolved_kwargs['data_source']
        )
        self.assertEqual(data_source.resolve_session(),
                         resolved_kwargs['session'].name)
        self.assertTrue(resolved_kwargs['session'].is_oppened)

    @served_by(MockSessionedService)
    def test_sessioned_with_my_data_source_closing_connection(self):
        """ Method resolve_from_data_source is anoteded with sessioned and
        datasource1 as parameter. We're overwriting the data_source parameter
        during the method call, changing to datasource2. It will be injected
        to the method kwargs a session from data_source1.
        """
        resolved_kwargs = (
            self.mock_sessioned_service.resolve_from_data_source(
                data_source="datasource2", close=True)
        )
        self.assertEqual("datasource2", resolved_kwargs['data_source'])
        data_source = self.data_connected.get_data_source(
            resolved_kwargs['data_source']
        )
        self.assertEqual(data_source.resolve_session(),
                         resolved_kwargs['session'].name)
        self.assertFalse(resolved_kwargs['session'].is_oppened)


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
        self.assertEqual(data_connected, self.data_connected_instance)

    def test_data_connected_from_service_recursively(self):
        data_connected = (self.served_by_instance.
                          get_service_data_connected_recursively())
        self.assertEqual(data_connected, self.data_connected_instance)

    def test_data_connected_from_service_none(self):
        mock_service = MockTestService(None)
        data_connected = mock_service.data_connected
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
        mock_service = MockTestService(None)
        data_sources = mock_service.get_data_sources()
        self.assertIsNone(data_sources)
