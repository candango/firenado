#!/usr/bin/env python
#
# Copyright 2015-2017 Flavio Garcia
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
        if data_sources in firenado.conf.data['sources']:
            logger.debug("Found data source [%s] in the list. Preceding with "
                         "the configuration process." % data_sources)
            config = firenado.conf.data['sources'][data_sources]
            connection_handler_config = firenado.conf.data['connectors'][
                config['connector']]
            module = importlib.import_module(connection_handler_config['module'])
            handler_class = getattr(module, connection_handler_config['class'])
            data_source_instance = handler_class(data_connected)
            config = data_source_instance.process_config(config)
            data_source_instance.configure(config)
            data_connected.set_data_source(data_sources, data_source_instance)
        else:
            logger.fatal("It was not possible to find [%s] in the list of "
                         "available data sources. Please fix the firenado "
                         "configuration file. Sometimes that could be only a "
                         "typo in one of app data sources to be created. Look "
                         "at app.data.sources list." % data_sources)
            sys.exit(errno.ENOKEY)
        # TODO: Testing the connection
        # Without that the error will just happen during the handler execution
    elif isinstance(data_sources, list):
        for data_source in data_sources:
            configure_data_sources(data_source, data_connected)
    # TODO Throw an error here if it is not string or list


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
        """ Returns the configured and connected database connection.
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
            logger.fatal("Error trying to connect to redis: %s", error)
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
        super(SqlalchemyConnector, self).__init__(data_connected)
        self.__connection = {
            'backend': None,
        }
        self.__engine = None

    def configure(self, config):
        from sqlalchemy import create_engine
        from sqlalchemy import exc, event, select
        # We will set the isolation level to READ UNCOMMITTED by default
        # to avoid the "cache" effect sqlalchemy has without this option.
        # Solution from: http://bit.ly/2bDq0Nv
        # TODO: Get the isolation level from data source config
        engine_params = {
            'isolation_level': "READ UNCOMMITTED"
        }
        if 'backend' in config:
            if config['backend'] == 'mysql':
                # Setting connection default connection timeout for mysql
                # backends as suggested on http://bit.ly/2bvOLxs
                # TODO: ignore this if pool_recycle is defined on config
                engine_params['pool_recycle'] = 3600

        self.__engine = create_engine(config['url'],
                                                    **engine_params)
        # Adding ping connection event handler as described at the pessimistic
        # disconnect section of: http://bit.ly/2c8Sm2t
        @event.listens_for(self.__engine, "engine_connect")
        def ping_connection(connection, branch):
            logger.debug("Pinging sqlalchemy connection.")
            if branch:
                # "branch" refers to a sub-connection of a connection,
                # we don't want to bother pinging on these.
                logger.debug("The connection is a branch. There is no need to "
                             "ping those.")
                return
            # turn off "close with result".  This flag is only used with
            # "connectionless" execution, otherwise will be False in any case
            save_should_close_with_result = connection.should_close_with_result
            connection.should_close_with_result = False
            try:
                # run a SELECT 1.   use a core select() so that
                # the SELECT of a scalar value without a table is
                # appropriately formatted for the backend
                logger.debug("Testing sqlalchemy connection.")
                connection.scalar(select([1]))
            except exc.DBAPIError as err:
                logger.warning(err)
                logger.warning("Firenado will try to reestablish the data "
                               "source connection.")
                # catch SQLAlchemy's DBAPIError, which is a wrapper
                # for the DBAPI's exception.  It includes a
                # .connection_invalidated attribute which specifies if this
                # connection is a "disconnect" condition, which is based on
                # inspection of the original exception by the dialect in use.
                if err.connection_invalidated:
                    # run the same SELECT again - the connection will
                    # re-validate itself and establish a new connection.
                    # The disconnect detection here also causes the whole
                    # connection pool to be invalidated so that all stale
                    # connections are discarded.
                    connection.scalar(select([1]))
                    logger.warning("Data source connection reestablished.")
                else:
                    raise
            finally:
                # restore "close with result"
                connection.should_close_with_result = \
                    save_should_close_with_result

        logger.info("Connecting to the database using the engine: %s.",
                    self.__engine)
        self.__connection['backend'] = config['backend']
        # will just happen during the handler execution

    def get_connection(self):
        return self.__connection

    def connect_engine(self):
        from sqlalchemy.exc import OperationalError
        try:
            self.__engine.connect()
        except OperationalError as op_error:
            logger.fatal("Error trying to connect to database: %s", op_error)
            sys.exit(errno.ECONNREFUSED)

    def get_a_session(self):
        from firenado.util.sqlalchemy_util import Session
        Session.configure(bind=self.__engine)
        return Session()

    @property
    def backend(self):
        return self.__connection['backend']

    @property
    def engine(self):
        return self.__engine

    @property
    def session(self):
        return self.get_a_session()

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
