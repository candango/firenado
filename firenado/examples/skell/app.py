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

import skell.handlers
import firenado.tornadoweb
from firenado import service
from skell import uimodules


class SkellComponent(firenado.tornadoweb.TornadoComponent):

    def get_handlers(self):
        import firenado.conf
        default_login = firenado.conf.app['login']['urls']['default']
        return [
            (r"/", skell.handlers.IndexHandler),
            (r"/session/counter", skell.handlers.SessionCounterHandler),
            (r"/session/timeout", skell.handlers.SessionTimeoutHandler),
            (r"/pagination", skell.handlers.PaginationHandler),
            (r"/%s" % default_login, skell.handlers.LoginHandler),
            (r"/private", skell.handlers.PrivateHandler),
        ]

    def get_ui_modules(self):
        return uimodules

    def initialize(self):
        import firenado.conf
        firenado.conf.app['login']['urls']['buga'] = 'buga'

    @service.served_by("skell.services.UserService")
    def install(self):
        """  Installing test database
        """
        from firenado.util.sqlalchemy_util import Base
        print('Installing Diasporapy Pod...')
        print('Creating Pod ...')
        engine = self.application.get_data_source(
            'test').engine
        engine.echo = True
        # Dropping all
        # TODO Not to drop all if something is installed right?
        Base.metadata.drop_all(engine)
        # Creating database
        Base.metadata.create_all(engine)
        self.user_service.create({
            'username': "Test",
            'first_name': "Test",
            'last_name': "User",
            'password': "testpass",
            'email': "test@test.ts"
        })

    def get_data_sources(self):
        return self.application.data_sources
