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

from datetime import datetime
from tests.service_test import TestableDataConnected, ServedByInstance
from firenado.sqlalchemy import base_to_dict, with_session
from firenado.service import FirenadoService, with_service
from sqlalchemy import String
from sqlalchemy.types import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import text
import unittest


class Base(DeclarativeBase):
    pass


class TestBase(Base):

    __tablename__ = "test"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False,
                                              server_default=text("now()"))
    modified: Mapped[datetime] = mapped_column(DateTime, nullable=False,
                                               server_default=text("now()"))


class MockSessionedService(FirenadoService):

    @with_session
    def resolve_from_default_data_source(self, **kwargs):
        return kwargs

    @with_session(data_source="datasource1")
    def resolve_from_data_source(self, **kwargs):
        return kwargs

    @property
    def default_data_source(self):
        return "datasource2"


class BaseToDictTestCase(unittest.TestCase):

    def setUp(self):
        self.test_object = TestBase()
        self.test_object.id = 1
        self.test_object.username = "anusername"
        self.test_object.password = "apassword"
        self.test_object.first_name = "Test"
        self.test_object.last_name = "Object"
        self.test_object.email = "test@example.com"

    def test_base_to_dict(self):
        dict_from_base = base_to_dict(self.test_object)
        self.assertEqual(dict_from_base['id'], self.test_object.id)
        self.assertEqual(dict_from_base['username'], self.test_object.username)
        self.assertEqual(dict_from_base['password'], self.test_object.password)
        self.assertEqual(dict_from_base['first_name'],
                         self.test_object.first_name)
        self.assertEqual(dict_from_base['last_name'],
                         self.test_object.last_name)
        self.assertEqual(dict_from_base['email'], self.test_object.email)
        self.assertEqual(dict_from_base['created'], self.test_object.created)
        self.assertEqual(dict_from_base['modified'], self.test_object.modified)

    def test_base_to_dict_parametrized(self):
        dict_from_base = base_to_dict(self.test_object,
                                      ["id", "username", "first_name"])
        self.assertEqual(dict_from_base['id'], self.test_object.id)
        self.assertEqual(dict_from_base['username'], self.test_object.username)
        self.assertEqual(dict_from_base['first_name'],
                         self.test_object.first_name)
        self.assertTrue("password" not in dict_from_base)
        self.assertTrue("last_name" not in dict_from_base)
        self.assertTrue("email" not in dict_from_base)
        self.assertTrue("created" not in dict_from_base)
        self.assertTrue("modified" not in dict_from_base)


class SessionedTestCase(unittest.TestCase):

    mock_sessioned_service: MockSessionedService

    def setUp(self):
        """ Setting up an object that has firenado.core.service.served_by
        decorators on some methods.
        """
        self.data_connected_instance = TestableDataConnected()
        self.served_by_instance = ServedByInstance(
            self.data_connected_instance)

    @property
    def data_connected(self):
        return self.served_by_instance.data_connected

    @with_service(MockSessionedService)
    def test_sessioned_default_data_source(self):
        """ Method resolve_from_default_data_source is anoteded with sessioned
        and no parameter. The data source to be used is the one defined either
        in the property or method named default_data_source. In this case we're
        using a property.

        As no session was provided the session will be closed
        """
        resolved_kwargs = (
            self.mock_sessioned_service.resolve_from_default_data_source()
        )
        self.assertEqual("datasource2", resolved_kwargs['data_source'])
        data_source = self.data_connected.get_data_source(
            resolved_kwargs['data_source']
        )
        self.assertEqual(data_source.resolve_session(),
                         resolved_kwargs['session'].name)
        self.assertFalse(resolved_kwargs['session'].is_oppened)

    @with_service(MockSessionedService)
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

    @with_service(MockSessionedService)
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
        self.assertFalse(resolved_kwargs['session'].is_oppened)

    @with_service(MockSessionedService)
    def test_sessioned_from_data_source_provide_session(self):
        """ Method resolve_from_default_data_source is anoteded with sessioned
        and no parameter. This time we provide the session and provided to
        close the datasource after executing resolve_from_data_source.
        """
        data_source = self.data_connected.get_data_source("datasource2")
        resolved_kwargs = (
            self.mock_sessioned_service.resolve_from_data_source(
                session=data_source.session, close=True
            )
        )
        # No datasource will be added to the kwards
        self.assertIsNone(resolved_kwargs.get("data_source"))
        # Using session provided
        self.assertEqual(data_source.resolve_session(),
                         resolved_kwargs['session'].name)
        self.assertFalse(resolved_kwargs['session'].is_oppened)

    @with_service(MockSessionedService)
    def test_sessioned_with_my_data_source_closing_connection(self):
        """ Method resolve_from_data_source is anoteded with sessioned and
        datasource1 as parameter. We're overwriting the data_source parameter
        during the method call, changing to datasource2. It will be injected
        to the method kwargs a session from data_source1.
        """
        resolved_kwargs = (
            self.mock_sessioned_service.resolve_from_data_source(
                data_source="datasource2")
        )
        self.assertEqual("datasource2", resolved_kwargs['data_source'])
        data_source = self.data_connected.get_data_source(
            resolved_kwargs['data_source']
        )
        self.assertEqual(data_source.resolve_session(),
                         resolved_kwargs['session'].name)
        self.assertFalse(resolved_kwargs['session'].is_oppened)
