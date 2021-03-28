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

import unittest
from firenado import data
from sqlalchemy.engine import base as base_engine
from sqlalchemy.future import engine as future_engine


class MockDataConnected(data.DataConnectedMixin):
    """ Data connected mock object. This object holds the data sources to be
    used in the test cases.
    """
    def __init__(self):
        pass


class SqlalchemyConnectorTestCase(unittest.TestCase):
    """ Case that tests an Firenado application after being loaded from its
    configuration file.
    """

    def setUp(self):
        """ Setting up an object that has firenado.core.service.served_by
        decorators on some methods.
        """
        self.data_connected_instance = MockDataConnected()

    def test_engine_not_future(self):
        """ Test if the engine created will be the base one if future is set
        as False or not set in the data source configuration. """
        data_source_conf = {
            'connector': "sqlalchemy",
            'url': "mysql+pymysql://root@localhost:3306/test",
            'future': False
        }
        data_source = data.config_to_data_source(data_source_conf,
                                                 self.data_connected_instance)
        self.assertTrue(isinstance(data_source.engine, base_engine.Engine))
        data_source_conf = {
            'connector': "sqlalchemy",
            'url': "mysql+pymysql://root@localhost:3306/test"
        }
        data_source = data.config_to_data_source(data_source_conf,
                                                 self.data_connected_instance)
        self.assertTrue(isinstance(data_source.engine, base_engine.Engine))

    def test_engine_future(self):
        """ Test if the engine created will be the future one if future is set
        as True in the data source configuration. """
        data_source_conf = {
            'connector': "sqlalchemy",
            'url': "mysql+pymysql://root@localhost:3306/test",
            'future': True
        }
        data_source = data.config_to_data_source(data_source_conf,
                                                 self.data_connected_instance)
        self.assertTrue(isinstance(data_source.engine, future_engine.Engine))
