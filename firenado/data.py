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

import errno
import functools
import importlib
import logging
import sys

from six import string_types, text_type


logger = logging.getLogger(__name__)


def configure_data_sources(data_sources, data_connected):
    """
    Configures data sources to a data connected object.
    :param data_sources: List of data sources to be configured
    :param data_connected: Data connected object where the data sources will
    be configured.
    """
    if isinstance(data_sources, (string_types, text_type)):
        import firenado.conf
        # TODO Handler unknow connection instance here
        config = firenado.conf.data['sources'][data_sources]
        connection_handler_config = firenado.conf.data['connectors'][
            config['connector']]
        module = importlib.import_module(connection_handler_config['module'])
        handler_class = getattr(module, connection_handler_config['class'])
        data_source_instance = handler_class(data_connected)
        config = data_source_instance.process_config(config)
        data_source_instance.configure(config)
        data_connected.set_data_source(data_sources, data_source_instance)
        # Testing the connection
        # Without that the error will just happen during the handler execution
    elif isinstance(data_sources, list):
        for data_source in data_sources:
            configure_data_sources(data_source, data_connected)
    #TODO Throw an error here if it is not string or list


def configure(data_sources):
    """ Decorator that configures data sources on a data connected object.
    :param data_sources: List of data sources to be configured.
    """
    def f_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            configure_data_sources(data_sources, self)
            return method(self, *args, **kwargs)
        return wrapper
    return f_wrapper


class DataConnectedMixin(object):
    """ Data connected objects has data sources. This mixin prepares an
    object to to have data sources set to it and retrieved from it.

    Example:
    >>> class MyClass(..., DataConnectedMixin):
    """

    @property
    def data_sources(self):
        """ Returns all connectors registered to the data connected instance.
        """
        return get_data_sources(self, '__data_sources')

    def get_data_source(self, name):
        """ Returns a data source by it's name.
        """
        return self.data_sources[name]

    def set_data_source(self, name, data_source):
        """ Add a data source to the data sources collection.
        """
        self.data_sources[name] = data_source


def get_data_sources(obj, data_sources_attribute):
    if not hasattr(obj, data_sources_attribute):
        setattr(obj, data_sources_attribute, {})
    return getattr(obj, data_sources_attribute)


class Connector(object):
    """ A connector will receive a data connection instance and provide
    a proper database connection to it.
    """

    def __init__(self, data_connected):
        self.__data_connected = data_connected

    def get_connection(self):
        """ Returns the configured and connected database conection.
        """
        return None

    def process_config(self, config):
        """ Parse the configuration data provided by the firenado.conf engine.
        """
        return {}


class LdapConnector(Connector):

    def __init__(self, data_connected):
        super(LdapConnector, self).__init__(data_connected)


class RedisConnector(Connector):
    """ Connects a redis database to a data connected instance.
    """

    def __init__(self, data_connected):
        self.__connection = None
        super(RedisConnector, self).__init__(data_connected)

    def configure(self, config):
        logger.info("Connecting to redis using the configuration: %s.", config)
        import redis
        redis_config = dict()
        redis_config.update(config)
        redis_config.pop("connector")
        # TODO Handle connection error
        self.__connection = redis.Redis(**redis_config)
        try:
            self.__connection.ping()
        except redis.ConnectionError as error:
            logger.error("Error trying to connect to redis: %s", error)
            sys.exit(errno.ECONNREFUSED)

    def get_connection(self):
        return self.__connection

    def process_config(self, config):
        db_config = {
            'connector': 'redis',
            'host': 'localhost',
            'port': 6379,
            'db': 0,
        }
        for key in config:
            if key in ['db', 'host', 'port']:
                if key in ['db', 'port']:
                    db_config[key] = int(config[key])
                db_config[key] = config[key]
        return db_config


class SqlalchemyConnector(Connector):
    """ Connects a sqlalchemy engine to a data connected instance. Sqlalchemy
    support a big variety of relational database backends. The connection
    returned by this handler contains a engine and session created by
    sqlalchemy and the database backend name.
    """

    def __init__(self, data_connected):
        self.__connection = {
            'engine': None,
            'session': None,
            'backend': None,
        }
        super(SqlalchemyConnector, self).__init__(data_connected)

    def configure(self, config):
        from sqlalchemy import create_engine
        from sqlalchemy.exc import OperationalError
        from firenado.util.sqlalchemy_util import Session

        self.__connection['engine'] = create_engine(config['url'])
        logger.info("Connecting to the database using the engine: %s.",
                    self.__connection['engine'])
        try:
            self.__connection['engine'].connect()
        except OperationalError as error:
            logger.error("Error trying to connect to database: %s", error)
            sys.exit(errno.ECONNREFUSED)

        Session.configure(bind=self.__connection['engine'])
        self.__connection['session'] = Session()
        self.__connection['backend'] = config['backend']
        # TODO: Test the session right here. Without that the error
        # will just happen during the handler execution

    def get_connection(self):
        return self.__connection

    @property
    def backend(self):
        return self.__connection['backend']

    @property
    def engine(self):
        return self.__connection['engine']

    @property
    def session(self):
        return self.__connection['session']

    def process_config(self, config):
        db_config = {
            'type': 'sqlalchemy',
        }
        for key in config:
            # TODO Need to handle other properies and create the url if needed.
            if key in ['url']:
                db_config[key] = config[key]
        # TODO: Handler errors here
        db_config['backend'] = db_config['url'].split(':')[0].split('+')[0]
        return db_config
