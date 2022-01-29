# -*- coding: UTF-8 -*-
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

from cartola import config
import errno
import firenado.conf
import functools
import logging
import sys

logger = logging.getLogger(__name__)


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

    def process_config(self, conf):
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
        self.__name = None

    def configure(self, name, conf):
        self.__name = name
        logger.info("Connecting to redis using the configuration: %s.", conf)
        import redis
        redis_conf = dict()
        redis_conf.update(conf)
        redis_conf.pop("connector")
        # TODO Handle connection error
        self.__connection = redis.Redis(**redis_conf)
        try:
            self.__connection.ping()
        except redis.ConnectionError as error:
            logger.fatal("Error trying to connect to redis: %s", error)
            sys.exit(errno.ECONNREFUSED)

    def get_connection(self):
        return self.__connection

    def process_config(self, conf):
        db_conf = {
            'connector': 'redis',
            'host': 'localhost',
            'port': 6379,
            'db': 0,
        }
        for key in conf:
            if key in ['db', 'host', 'port']:
                if key in ['db', 'port']:
                    db_conf[key] = int(conf[key])
                db_conf[key] = conf[key]
        return db_conf


class SqlalchemyConnector(Connector):
    """ Connects a sqlalchemy engine to a data connected instance. Sqlalchemy
    support a big variety of relational database backends. The connection
    returned by this handler contains a engine and session created by
    sqlalchemy and the database backend name.
    """

    def __init__(self, data_connected):
        super(SqlalchemyConnector, self).__init__(data_connected)
        self.__name = None
        self.__connection = {
            'backend': None,
            'session': {
                'autoflush': True,
                'autocommit': False,
                'expire_on_commit': True,
                'info': None
            }
        }
        self.__engine = None

    def configure(self, name, conf):
        self.__name = name
        from sqlalchemy import create_engine
        from sqlalchemy import exc, event, select
        # We will set the isolation level to READ UNCOMMITTED by default
        # to avoid the "cache" effect sqlalchemy has without this option.
        # Solution from: http://bit.ly/2bDq0Nv
        # TODO: Get the isolation level from data source conf
        engine_params = {
            'isolation_level': "READ UNCOMMITTED"
        }

        if "backend" in conf:
            if conf['backend'] == 'mysql':
                # Setting connection default connection timeout for mysql
                # backends as suggested on http://bit.ly/2bvOLxs
                # TODO: ignore this if pool_recycle is defined on conf
                engine_params['pool_recycle'] = 3600

        if "future" in conf:
            if conf['future']:
                engine_params['future'] = True

        if "pool" in conf:
            if "size" in conf['pool']:
                engine_params['pool_size'] = conf['pool']['size']
            if "max_overflow" in conf['pool']:
                engine_params['max_overflow'] = conf['pool']['max_overflow']
            if "class" in conf['pool']:
                engine_params['pool_class'] = conf['pool']['class']
                if isinstance(engine_params['pool_class'], str):
                    engine_params['pool_class'] = config.get_from_string(
                        engine_params['pool_class'])

        if "session" in conf:
            if "autoflush" in conf['session']:
                self.__connection['session']['autoflush'] = conf['session'][
                    'autoflush']
            if "autocommit" in conf['session']:
                self.__connection['session']['autocommit'] = conf['session'][
                    'autocommit']
            if "expire_on_commit" in conf['session']:
                self.__connection['session']['expire_on_commit'] = conf[
                    'session']['expire_on_commit']
            if "info" in conf['session']:
                self.__connection['session']['info'] = conf['session']['info']

        if "url" not in conf:
            print(self.__connection)
            logger.error("It is not possible to create sqlalchemy engine for "
                         "%s datasource. Configuration: %s." %
                         (self.__name, conf))

        self.__engine = create_engine(conf['url'], **engine_params)

        @event.listens_for(self.__engine, "engine_connect")
        def ping_connection(connection, branch):
            # Adding ping connection event handler as described at the
            # pessimistic disconnect section of: http://bit.ly/2c8Sm2t
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
                connection.should_close_with_result = (
                    save_should_close_with_result)
        logger.info("Connecting to the database using the engine: %s.",
                    self.__engine)
        self.__connection['backend'] = conf['backend']
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

    def get_a_session(self, autoflush=True, autocommit=False,
                      expire_on_commit=True, info=None):
        from firenado.util.sqlalchemy_util import Session
        Session.configure(bind=self.__engine, autoflush=autoflush,
                          autocommit=autocommit,
                          expire_on_commit=expire_on_commit, info=info)
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

    def process_config(self, conf):
        db_conf = {
            'type': 'sqlalchemy',
        }
        for key in conf:
            # TODO Handle other properties and create the url if needed.
            if key in ["db", "database", "dialect", "driver", "future", "host",
                       "pass", "password", "pool", "port", "session", "url",
                       "user", "username"]:
                index = key
                if index == "db":
                    index = "database"
                if index == "user":
                    index = "username"
                if index == "pass":
                    index = "password"
                db_conf[index] = conf[key]
        # TODO: Handler errors here
        if "url" in db_conf:
            db_conf['backend'] = db_conf['url'].split(':')[0].split('+')[0]
        else:
            url = ""
            if "dialect" in db_conf:
                db_conf['backend'] = db_conf['dialect']
                url = "%s" % db_conf.pop("dialect")
                if "driver" in db_conf:
                    url = "%s+%s" % (url, db_conf.pop("driver"))
            if "username" in db_conf:
                url = "%s://%s" % (url, db_conf.pop("username"))
                if "password" in db_conf:
                    from urllib.parse import quote
                    url = "%s:%s" % (url, quote(db_conf.pop("password")))
            if "host" in db_conf:
                url = "%s@%s" % (url, db_conf.pop("host"))
                if "port" in db_conf:
                    url = "%s:%s" % (url, db_conf.pop("port"))
            if "database" in db_conf:
                url = "%s/%s" % (url, db_conf.pop("database"))
            db_conf['url'] = url
        return db_conf


def config_to_data_source(name, conf, data_connected):
    """ Convert a data source conf to it's respective data source. We need
    a data connected to use while instantiating the data source.
    :param name: Datasource name
    :param conf: A data source confuration item
    :param data_connected: A data connected object
    :return: Connector
    """
    connector_conf = firenado.conf.data['connectors'][conf['connector']]
    # TODO: Test if handler was returned None. An error occurred.
    handler_class = config.get_from_module(connector_conf['module'],
                                           connector_conf['class'])
    data_source_instance = handler_class(data_connected)
    conf = data_source_instance.process_config(conf)
    data_source_instance.configure(name, conf)
    return data_source_instance


def configure_data_sources(data_sources, data_connected):
    """ Configure all data sources from configuration and set to the data
    connected.
    :param data_sources: List of data sources to be configured
    :param data_connected: Data connected object where the data sources will
    be configured.
    """
    if isinstance(data_sources, str):
        if data_sources in firenado.conf.data['sources']:
            logger.debug("Found data source [%s] in the list. Preceding with "
                         "the configuration process." % data_sources)
            conf = firenado.conf.data['sources'][data_sources]
            data_source_instance = config_to_data_source(
                data_sources, conf, data_connected)
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
