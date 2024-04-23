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

from . import handlers, services, uimodules
from firenado import tornadoweb
from firenado import data, service
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ComponentCustomErrorHandler(tornadoweb.TornadoErrorHandler):

    def handle_error(self, request: tornadoweb.TornadoHandler,
                     status_code: int, **kwargs: Any) -> None:
        request.set_status(status_code)
        request.render("error.html", http_error=kwargs.get('exc_info')[1])


class TestappComponent(tornadoweb.TornadoComponent):

    user_service: services.LoginService

    def __init__(self, name, application):
        super(TestappComponent, self).__init__(name, application)
        self.user_service = None

    def get_error_handler(self) -> tornadoweb.TornadoErrorHandler:
        return ComponentCustomErrorHandler(self)

    def get_handlers(self):
        import firenado.conf
        default_login = firenado.conf.app['login']['urls']['default']
        return [
            (r"/", handlers.IndexHandler),
            (r"/async/timeout", handlers.AsyncTimeoutHandler),
            (r"/component/error", handlers.ComponentErrorHandler),
            (r"/handler/error", handlers.HandlerErrorHandler),
            (r"/session/counter", handlers.SessionCounterHandler),
            (r"/session/config", handlers.SessionConfigHandler),
            (r"/pagination", handlers.PaginationHandler),
            (r"/%s" % default_login, handlers.LoginHandler),
            (r"/%s" % default_login, handlers.LoginHandler),
            (r"/logout", handlers.LogoutHandler),
            (r"/private", handlers.PrivateHandler),
        ]

    def get_ui_modules(self):
        return uimodules

    def initialize(self):
        import firenado.conf
        firenado.conf.app['login']['urls']['buga'] = 'buga'
        data_source_conf = {
            'connector': "sqlalchemy",
            'url': "mysql+pymysql://root@localhost:3306/test",
            # 'isolation_level': 'REPEATABLE READ',
            'pool': {
                'size': 10,
                'max_overflow': 10,
                # 'pool_recycle': 400
            }
        }
        data_source_name = "test"
        data_source = data.config_to_data_source(data_source_name,
                                                 data_source_conf,
                                                 self.application)
        self.application.set_data_source(data_source_name, data_source)

    @service.served_by(services.UserService)
    def install(self):
        from sqlalchemy.engine import Engine
        """  Installing test database
        """
        from testapp.models import Base
        print('Installing Testapp App...')
        print('Creating App ...')
        engine: Engine = self.application.get_data_source(
            'test').engine
        engine.echo = True
        with engine.connect() as conn:
            # Dropping all
            # TODO Not to drop all if something is installed right?
            Base.metadata.drop_all(conn)
            # Creating database
            Base.metadata.create_all(conn)
            conn.commit()
        self.user_service.create({
            'username': "Test",
            'first_name': "Test",
            'last_name': "User",
            'password': "testpass",
            'email': "test@test.ts"
        })

    @property
    def data_connected(self):
        return self.application

    def after_request(self, handler):
        logging.info("Doing something after handler's request: %s" % handler)

    def before_request(self, handler):
        logging.info("Doing something before handler's request: %s" % handler)
