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

import sys


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
        """ Parse the configuration data provided by the iflux.conf engine.
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
        import redis
        redis_config = dict()
        redis_config.update(config)
        redis_config.pop("connector")
        # TODO Handle connection error
        self.__connection = redis.Redis(**redis_config)
        try:
            self.__connection.ping()
        except redis.ConnectionError as error:
            sys.exit()

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
        try:
            self.__connection['engine'].connect()
        except OperationalError as error:
            sys.exit()

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
