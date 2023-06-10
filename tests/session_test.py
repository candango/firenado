# -*- coding: UTF-8 -*-
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

import firenado.conf
from firenado.config import get_class_from_config
from firenado.tornadoweb import TornadoApplication
from tests import chdir_app
import unittest
import warnings


class FileSessionTestCase(unittest.TestCase):
    """ Case that tests a Firenado application after being loaded from its
    configuration file.
    """

    def setUp(self):
        """ Application configuration file will be read and components will be
        loaded.
        """
        chdir_app("file", "session")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.application = TornadoApplication()
            self.session_handler_config = firenado.conf.session[
                'handlers'][firenado.conf.session['type']]
            self.session_handler_config = firenado.conf.session[
                'handlers'][firenado.conf.session['type']]
            self.session_handler_class = get_class_from_config(
                self.session_handler_config)

    def test_defaults_session_parameters(self):
        """ Checks default session parameters on the configuration
        session section
        """
        self.assertEqual(firenado.conf.session['life_time'], 1800)
        self.assertEqual(firenado.conf.session['callback_time'], 120)

    def test_application_session_handler(self):
        """ Checks if the session handler loaded is the same the session
        handler defined.
        """
        self.assertEqual(
            self.application.session_engine.session_handler.__class__,
            self.session_handler_class
        )

    def test_session_type_file(self):
        """ Checks if test component was loaded correctly by the application
        __init__ method.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            application = TornadoApplication()
            session_handler_config = firenado.conf.session[
                'handlers'][firenado.conf.session['type']]
            session_handler_class = get_class_from_config(
                session_handler_config)
            self.assertEqual(
                application.session_engine.session_handler.__class__,
                session_handler_class)


class RedisSessionTestCase(unittest.TestCase):
    """ Tests a Firenado application after being loaded from its configuration
    file. """

    def setUp(self):
        """ Application configuration file will be read and components will be
        loaded.
        """
        chdir_app("redis", "session")

    def test_session_type_redis(self):
        """ Checks if test component was loaded correctly by the application
        __init__ method.
        """
        self.assertEqual(firenado.conf.session['enabled'], True)
        self.assertEqual(firenado.conf.session['type'], "redis")

    def test_custom_session_parameters(self):
        """ Checks default session parameters on the configuration
        session section
        """
        self.assertEqual(firenado.conf.session['life_time'], 1900)
        self.assertEqual(firenado.conf.session['callback_time'], 40)


class EncodersSessionTestCase(unittest.TestCase):

    def test_pickle_session_encoder(self):
        """ Checks if the pickle session encoder will keep a dict structure
        and values intact after encoding and decoding it.
        """
        from firenado.session import PickleSessionEncoder
        my_dict = {
            'value1': "My value1",
            'value2': {
                'value3': "My value3",
            }
        }
        encoder = PickleSessionEncoder()
        encoded_data = encoder.encode(my_dict)
        decoded_data = encoder.decode(encoded_data)
        self.assertEqual(decoded_data['value1'], my_dict['value1'])
        self.assertEqual(decoded_data['value2']['value3'],
                         my_dict['value2']['value3'])

    def test_json_session_encoder(self):
        """Checks if json session encoder will keep a dict structure and values
        intact after encoding and decoding it."""
        from firenado.session import JsonSessionEncoder
        my_dict = {
            'value1': "My value1",
            'value2': {
                'value3': "My value3",
            }
        }
        encoder = JsonSessionEncoder()
        encoded_data = encoder.encode(my_dict)
        decoded_data = encoder.decode(encoded_data)
        self.assertEqual(decoded_data['value1'], my_dict['value1'])
        self.assertEqual(decoded_data['value2']['value3'],
                         my_dict['value2']['value3'])
