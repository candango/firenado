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

from __future__ import (absolute_import, division,
                        print_function, with_statement)

import functools
import firenado.conf
from firenado.conf import get_class_from_config
from firenado.util import file, random_string
import tornado.web
import os


class SessionEngine(object):
    """SessionEngine provides session support to an application.
    """

    def __init__(self, session_aware_instance):
        # TODO: By the way session could be disabled. How do we 
        # handle that?
        # TODO: check if session type exists. Maybe disable it if type is not
        # defined. We need to inform the error here
        session_handler_class = get_class_from_config(
            firenado.conf.session['handlers'][firenado.conf.session['type']]
        )
        self.session_aware_instance = session_aware_instance
        self.session_handler = session_handler_class(self)
        self.session_handler.set_settings({})
        self.session_handler.configure()
        encoder_class = get_class_from_config(
            firenado.conf.session['encoders'][
                firenado.conf.session['encoder']
            ]
        )
        self.session_encoder = encoder_class()

    def get_session(self, request_handler):
        """Returns a valid session object. This session is handler by the
        session handler defined on the application configuration. """
        if firenado.conf.session['enabled']:
            session = Session(self)
            cookie_created_on_request = False
            session_id = SessionHandler.get_session_id_cookie(request_handler)
            if session_id is None:
                cookie_created_on_request = True
                session = self.__renew_session(request_handler)
            else:
                session.id = session_id
            # TODO: Check if the session is stored
            if not self.session_handler.is_session_stored(session_id):
                if not cookie_created_on_request:
                    # Regenerating the session id. Because the
                    # cookie was not created during at the same request
                    # the file is being created.
                    cookie_created_on_request = True
                    session = self.__renew_session(request_handler)
            if not cookie_created_on_request:
                session_data = self.decode_session_data(
                    self.session_handler.read_stored_session(session_id))
                session = Session(self, session_data, session_id)
            return session

    def store_session(self, request_handler):
        """Sends the session data to be stored by the session handler defined
        on the application configuration. """
        if firenado.conf.session['enabled']:
            session_id = request_handler.session.id
            # If session was destroyed than we gonna handle it differently
            # If session id is None than ignored (it is probably a redirect
            # leftover from security)
            if session_id is not None:
                if not request_handler.session.is_destroyed():
                    encoded_session_data = self.encode_session_data(
                        request_handler.session.get_data())
                    if request_handler.session.is_changed():
                        self.session_handler.write_stored_session(
                            session_id,
                            encoded_session_data
                        )
                else:
                    # Generating a new session
                    self.session_handler.destroy_stored_session(session_id)

    def encode_session_data(self, data):
        return self.session_encoder.encode(data)

    def decode_session_data(self, data):
        return self.session_encoder.decode(data)

    def get_session_aware_instance(self):
        return self.session_aware_instance

    def __renew_session(self, request_handler):
        if firenado.conf.session['enabled']:
            session = Session(self)
            session_id = SessionHandler.create_session_id_cookie(
                request_handler)
            session.id = session_id
            self.session_handler.create_session(
                session_id,
                self.encode_session_data(session.get_data())
            )
            return session
        return None


class SessionEnginedMixin(object):
    """
    This mixin includes a configured session engine to an entity.
    The engine will handle session reads and writes triggered by
    session engined entity.

    Example:
    >>> class MyApplication(firenado.core.TornadoApplication,
    >>>                     SessionEnginedMixin):

    Refer to SessionEngine documentation in order to know which methods are
    available.
    """

    @property
    def session_engine(self):
        """ Returns a SessionEngine instance """
        return create_session_engine(self, '__session_engine', SessionEngine)


class Session(object):

    def __init__(self, engine, data={}, id=None):
        self.__engine = engine
        self.id = id
        self.__data = data
        self.__destroyed = False
        self.__changed = False

    def clear(self):
        """ Clear all data stored into the session. This is not 
        renewing/creating a new session id. If you want that use 
        session.destroy() """
        self.__data.clear()
        self.__changed = True

    def destroy(self, request_handler):
        """ Clearing session data and marking the session to be
        renewed at the end of the request. """
        self.clear()
        self.__destroyed = True
        self.__engine.store_session(request_handler)

    def get(self, key):
        """ Returns the value from the session data by a given key """
        self.__lock_if_destroyed()
        if self.has(key):
            return self.__data[key]
        return None

    def get_data(self):
        self.__lock_if_destroyed()
        return self.__data.copy()

    def has(self, key):
        self.__lock_if_destroyed()
        """ Returns if session data has some data stored by a given key. """
        return self.__data.has_key(key)

    def delete(self, key):
        self.__lock_if_destroyed()
        if key in self.__data:
            del self.__data[key]
            self.__changed = True

    def is_destroyed(self):
        """ Returns is the session is marked to be destroyed 
        during session storing procedure. """
        return self.__destroyed

    def is_changed(self):
        return self.__changed

    def __lock_if_destroyed(self):
        if self.is_destroyed():
            raise SessionDestroyedError()

    def set(self, key, value):
        """ Set a value into the session data labeled by a given key """
        self.__lock_if_destroyed()
        self.__data[key] = value
        self.__changed = True


class SessionDestroyedError(tornado.web.HTTPError):

    def __init__(self, status_code, log_message=None, *args, **kwargs):
        message = "The session was destroyed. It is necessary a renew the " \
                  "session before use it again."
        super(SessionDestroyedError, self).__init__(
            505, message, *args, **kwargs)


class SessionHandler(object):

    def __init__(self, engine):
        self.engine = engine
        self.settings = {}

    def create_session(self, session_id, data):
        pass

    def read_stored_session(self, session_id):
        pass

    def write_stored_session(self, session_id, data):
        pass

    def destroy_stored_session(self, session_id):
        pass

    @staticmethod
    def create_session_id_cookie(request_handler):
        session_id = SessionHandler.__generate_session_id()
        request_handler.set_cookie(
            firenado.conf.session['name'], session_id,
            **SessionHandler.__session_id_cookie_settings())
        return session_id

    @staticmethod
    def get_session_id_cookie(request_handler):
        return request_handler.get_cookie(firenado.conf.session['name'])

    def is_session_stored(self, session_id):
        pass

    def configure(self):
        pass

    def set_settings(self, settings):
        self.settings = settings

    @staticmethod
    def __session_id_cookie_settings():
        """ Defines some settings to be used with the session id cookie. """
        cookie_settings = {}
        cookie_settings.setdefault('expires', None)
        cookie_settings.setdefault('expires_days', None)
        return cookie_settings

    @staticmethod
    def __generate_session_id():
        # TODO we should make this generation more secure
        # TODO I think this is a good place to put a customized session
        # generator based on the configuration
        return random_string(64)


def create_session_engine(obj, session_engine_attribute, session_engine_class):
    if not hasattr(obj, session_engine_attribute):
        session_engine_instance = session_engine_class(obj)
        setattr(obj, session_engine_attribute, session_engine_instance)
    return getattr(obj, session_engine_attribute)


def read(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        session = self.application.session_engine.get_session(self)
        self.session = session
        return method(self, *args, **kwargs)
    return wrapper


def write(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.application.session_engine.store_session(self)
        return method(self, *args, **kwargs)
    return wrapper


class FileSessionHandler(SessionHandler):
    """
    Session handler that deals with file data stored in files.

    The FileSessionHandler blocks tornado requests as long we are reading and
    writing files. We will try to minimize the blocking effect but by now don't
    use this for high traffic sites.
    """

    path = None

    def configure(self):
        if os.path.exists(firenado.conf.session['file']['path']):
            self.path = firenado.conf.session['file']['path']
        else:
            # TODO: Need to think about this. I don't know if this is a
            # good behaviour. Maybe just crash the app here
            # or disable the session with a good warning.
            self.path = firenado.conf.APP_TMP_PATH

    def create_session(self, session_id, data):
        # TODO: What could possibly go wrong here? Let's handle it!
        session_file = os.path.join(self.path, self.__get_filename(session_id))
        if os.path.exists(firenado.conf.session['file']['path']):
            file.touch(session_file)
            file.write(session_file, data)

    def read_stored_session(self, session_id):
        session_file = os.path.join(self.path, self.__get_filename(session_id))
        return file.read(session_file)

    def write_stored_session(self, session_id, data):
        session_file = os.path.join(self.path, self.__get_filename(session_id))
        file.write(session_file, data)

    def destroy_stored_session(self, session_id):
        try:
            session_file = os.path.join(
                self.path,
                self.__get_filename(session_id)
            )
            os.remove(session_file)
        except OSError:
            # TODO Why we are deleting the session file twice?
            pass

    def is_session_stored(self, session_id):
        return os.path.isfile(os.path.join(self.path, self.__get_filename(
            session_id)))

    def __get_filename(self, session_id):
        return 'firenado_%s.sess' % session_id


class RedisSessionHandler(SessionHandler):
    """
    Session handler that deals with file data stored  in a redis database.
    """

    data_source = None

    def configure(self):
        self.data_source = self.engine.get_session_aware_instance().\
            get_data_source(firenado.conf.session['redis']['data']['source'])

    def create_session(self, session_id, data):
        self.write_stored_session(session_id, data)

    def read_stored_session(self, session_id):
        return self.data_source.get_connection().get(
            self.__get_key(session_id))

    def write_stored_session(self, session_id, data):
        self.data_source.get_connection().set(
            self.__get_key(session_id), data)

    def destroy_stored_session(self, session_id):
        key = self.__get_key(session_id)
        self.data_source.get_connection().delete(key)

    def is_session_stored(self, session_id):
        return self.data_source.get_connection().get(
            self.__get_key(session_id)) is not None

    def __get_key(self, session_id):
        return '%s:%s' % (firenado.conf.session['redis']['prefix'], session_id)


class SessionEncoder(object):

    def encode(self, data):
        return data

    def decode(self, data):
        return data


class PickeSessionEncoder(SessionEncoder):

    def encode(self, data):
        import pickle
        return pickle.dumps(data, 2)

    def decode(self, data):
        import pickle
        return pickle.loads(data)
