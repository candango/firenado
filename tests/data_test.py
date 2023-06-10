#!/usr/bin/env python
#
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

from cartola import config
import unittest
from firenado import data
import firenado.conf
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
        data_source_name = "not_future_data_source"
        data_source_conf = {
            'connector': "sqlalchemy",
            'url': "mysql+pymysql://root@localhost:3306/test",
            'future': False
        }
        data_source = data.config_to_data_source(data_source_name,
                                                 data_source_conf,
                                                 self.data_connected_instance)
        self.assertTrue(isinstance(data_source.engine, base_engine.Engine))
        data_source_conf = {
            'connector': "sqlalchemy",
            'url': "mysql+pymysql://root@localhost:3306/test"
        }
        data_source = data.config_to_data_source(data_source_name,
                                                 data_source_conf,
                                                 self.data_connected_instance)
        self.assertTrue(isinstance(data_source.engine, base_engine.Engine))

    def test_engine_future(self):
        """ Test if the engine created will be the future one if future is set
        as True in the data source configuration. """
        data_source_name = "future_data_source"
        data_source_conf = {
            'connector': "sqlalchemy",
            'url': "mysql+pymysql://root@localhost:3306/test",
            'future': True
        }
        data_source = data.config_to_data_source(data_source_name,
                                                 data_source_conf,
                                                 self.data_connected_instance)
        self.assertTrue(isinstance(data_source.engine, future_engine.Engine))

    def test_parametrized_instead_url(self):
        """ Test a parametrized data source configuration will generate a
        valid sqlalchemy connection url."""
        connector_conf = firenado.conf.data['connectors']["sqlalchemy"]
        handler_class = config.get_from_module(connector_conf['module'],
                                               connector_conf['class'])
        data_source_instance = handler_class(self.data_connected_instance)

        # At this point the connector parameter doesn't matter because we
        # already have the handler class instantiated correctly.
        # Keeping it at the data_source conf just for the sake of clarity.
        url_all_parameters = "mysql+pymysql://root:apass@localhost:3306/test"
        conf = data_source_instance.process_config({
            'connector': "sqlalchemy",
            'dialect': "mysql",
            'driver': "pymysql",
            'username': "root",
            'password': "apass",
            'host': "localhost",
            'port': "3306",
            'database': "test"
        })
        self.assertEqual(url_all_parameters, conf['url'])

        url_no_password = "mysql+pymysql://root@localhost:3306/test"
        conf = data_source_instance.process_config({
            'connector': "sqlalchemy",
            'dialect': "mysql",
            'driver': "pymysql",
            'user': "root",  # using user instead username
            'host': "localhost",
            'port': "3306",
            'database': "test"
        })
        self.assertEqual(url_no_password, conf['url'])

        url_no_port = "mysql+pymysql://root:apass@localhost/test"
        conf = data_source_instance.process_config({
            'connector': "sqlalchemy",
            'dialect': "mysql",
            'driver': "pymysql",
            'username': "root",
            'pass': "apass",  # using pass instead of password
            'host': "localhost",
            'db': "test"  # using db instead of database
        })
        self.assertEqual(url_no_port, conf['url'])
