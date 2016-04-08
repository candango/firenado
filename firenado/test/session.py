#!/usr/bin/env python
#
# Copyright 2015-2016 Flavio Garcia
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

import unittest

import firenado.conf
from firenado.config import get_class_from_config
from firenado.test import chdir_app
from firenado.tornadoweb import TornadoApplication


class FileSessionTestCase(unittest.TestCase):
    """ Case that tests an Firenado application after being loaded from its
    configuration file.
    """

    def setUp(self):
        """ Application configuration file will be read and components will be
        loaded.
        """
        chdir_app('file', 'session')
        self.application = TornadoApplication()
        self.session_handler_config = firenado.conf.session[
            'handlers'][firenado.conf.session['type']]
        self.session_handler_config = firenado.conf.session[
            'handlers'][firenado.conf.session['type']]
        self.session_handler_class = get_class_from_config(
            self.session_handler_config)


    def test_application_session_handler(self):
        """ Checks if the session handler loaded is the same the session
        handler defined.
        """
        app_session_handler_class = \
            self.application.session_engine.session_handler.__class__
        self.assertEquals(
            app_session_handler_class, self.session_handler_class)



class SessionTestCase(unittest.TestCase):
    """ Case that tests an Firenado application after being loaded from its
    configuration file.
    """

    def test_session_type_file(self):
        """ Checks if test component was loaded correctly by the application
        __init__ method.
        """
        chdir_app('file', 'session')
        application = TornadoApplication()
        session_handler_config = firenado.conf.session[
            'handlers'][firenado.conf.session['type']]
        session_handler_class = get_class_from_config(session_handler_config)
        app_session_handler_class = \
            application.session_engine.session_handler.__class__
        self.assertEquals(app_session_handler_class, session_handler_class)
        print(str(session_handler_class))

        print(application.session_engine.session_handler.__class__)

        sess_handler_path = application.session_engine.session_handler.path

        sess_handler_path


    def test_session_type_redis(self):
        """ Checks if test component was loaded correctly by the application
        __init__ method.
        """
        chdir_app('redis', 'session')
        self.assertEquals(firenado.conf.session['enabled'], True)
        self.assertEquals(firenado.conf.session['type'], 'redis')
