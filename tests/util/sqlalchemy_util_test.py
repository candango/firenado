#!/usr/bin/env python
#
# Copyright 2015-2020 Flavio Garcia
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

from firenado.util.sqlalchemy_util import Base, base_to_dict
from sqlalchemy import Column, String
from sqlalchemy.types import Integer, DateTime
from sqlalchemy.sql import text
import unittest


class TestBase(Base):

    __tablename__ = "test"

    id = Column("id", Integer, primary_key=True)
    username = Column("username", String(150), nullable=False)
    first_name = Column("first_name", String(150), nullable=False)
    last_name = Column("last_name", String(150), nullable=False)
    password = Column("password", String(150), nullable=False)
    email = Column("email", String(150), nullable=False)
    created = Column("created", DateTime, nullable=False,
                     server_default=text("now()"))
    modified = Column("modified", DateTime, nullable=False,
                      server_default=text("now()"))


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

    def test_base_to_dict(self):
        dict_from_base = base_to_dict(self.test_object,
                                      ["id", "username", "first_name"])
        self.assertEqual(dict_from_base['id'], self.test_object.id)
        self.assertEqual(dict_from_base['username'], self.test_object.username)
        self.assertEqual(dict_from_base['first_name'],
                         self.test_object.first_name)
        self.assertTrue('password' not in dict_from_base)
        self.assertTrue('last_name' not in dict_from_base)
        self.assertTrue('email' not in dict_from_base)
        self.assertTrue('created' not in dict_from_base)
        self.assertTrue('modified' not in dict_from_base)
