# -*- coding: UTF-8 -*-
#
# Copyright 2015-2024 Flavio Garcia
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

from .services import LoginService, UserService

import firenado.conf
from firenado import security, service, tornadoweb
from firenado.util.sqlalchemy_util import base_to_dict
import hashlib
from tornado import escape, gen
from tornado.web import HTTPError
from typing import Any
import logging

logger = logging.getLogger(__name__)


class AuthHandler:

    def get_current_user(self):
        from tornado.escape import json_decode
        user_data = self.session.get("user")
        if user_data:
            return json_decode(user_data)
        return None


class HandlerCustomErrorHandler(tornadoweb.TornadoErrorHandler):

    def handle_error(self, request: tornadoweb.TornadoHandler,
                     status_code: int, **kwargs: Any) -> None:
        request.set_status(status_code)
        request.render("error.html", http_error=kwargs.get('exc_info')[1])


class AsyncTimeoutHandler(tornadoweb.TornadoHandler):

    def timed_out(self):
        self.render("async_timeout.html")

    @gen.coroutine
    def get(self):
        from tornado.util import TimeoutError
        try:
            yield gen.with_timeout(2, gen.sleep(5))
            self.write("This will never be reached!!")
        except TimeoutError as te:
            logger.warning(te.__repr__())
            self.timed_out()


class IndexHandler(AuthHandler, tornadoweb.TornadoHandler):

    def get(self):
        import firenado.conf
        default_login = firenado.conf.app['login']['urls']['default']
        self.render("index.html", message="Hello world!!!",
                    login_url=default_login)


class ComponentErrorHandler(tornadoweb.TornadoHandler):

    def get(self):
        raise HTTPError(400, "This is an error thrown by my handler and "
                             "handled by the component's error handler.",
                        reason="ComponentCustomErrorHandler is set at the "
                               "handler's component and be used by default.")


class HandlerErrorHandler(tornadoweb.TornadoHandler):

    def get_error_handler(self) -> tornadoweb.TornadoErrorHandler:
        return HandlerCustomErrorHandler(self)

    def get(self):
        raise HTTPError(400, "This is an error thrown by my handler and "
                             "handled by the handler's error handler.",
                        reason="HandlerCustomErrorHandler is set at the "
                               "current handler overwriting the component's "
                               "custom error handler.")


class SessionConfigHandler(tornadoweb.TornadoHandler):

    def get(self):
        self.render("session_config.html", session_conf=firenado.conf.session)


class SessionCounterHandler(tornadoweb.TornadoHandler):

    def get(self):
        reset = self.get_argument("reset", False, True)
        if reset:
            self.session.delete('counter')
            self.redirect(self.get_rooted_path("/session/counter"))
            return None
        counter = 0
        if self.session.has('counter'):
            counter = self.session.get('counter')
        counter += 1
        self.session.set('counter', counter)
        self.render("session.html", session_value=counter)


class LoginHandler(AuthHandler, tornadoweb.TornadoHandler):

    login_service: LoginService
    user_service: UserService

    def get(self):
        default_login = firenado.conf.app['login']['urls']['default']
        errors = {}
        if self.authenticated():
            self.redirect(self.get_rooted_path("private"))
            return
        if self.session.has('login_errors'):
            errors = self.session.get('login_errors')
        self.render("login.html", errors=errors,
                    login_url=default_login)

    # you can user either the class rererence or string
    @service.with_service(LoginService)
    @service.with_service("testapp.services.UserService")
    def post(self):
        self.session.delete('login_errors')
        default_login = firenado.conf.app['login']['urls']['default']
        username = self.get_argument('username')
        password = self.get_argument('password')
        errors = {}
        if username == "":
            errors['username'] = "Please inform the username"
        if password == "":
            errors['password'] = "Please inform the password"

        if not errors:
            if not self.login_service.is_valid(username, password):
                errors['fail'] = "Invalid login"
            else:
                user = self.user_service.by_username(username)
                user_data = base_to_dict(user, ['id', 'username', 'password',
                                                'first_name', 'last_name',
                                                'email'])
                # Shhhhh!!!! this is a secret.
                user_data['password'] = hashlib.sha256(
                    "_".join(user_data['password']).encode('ascii')
                ).hexdigest()
                self.session.set("user", escape.json_encode(user_data))
                self.redirect(self.get_rooted_path("private"))

        if errors:
            self.session.set('login_errors', errors)
            self.redirect(self.get_rooted_path(default_login))

    def after_request(self):
        logging.info("Doing something after the login handler's request.")

    def before_request(self):
        logging.info("Doing something before the login handler's request.")


class LogoutHandler(AuthHandler, tornadoweb.TornadoHandler):

    def get(self):
        default_login = firenado.conf.app['login']['urls']['default']
        if self.authenticated():
            self.session.destroy(self)
            self.redirect(self.get_rooted_path("private"))
        else:
            self.redirect(self.get_rooted_path(default_login))
        return


class PrivateHandler(AuthHandler, tornadoweb.TornadoHandler):

    @security.authenticated
    def get(self):
        user_data = escape.json_decode(self.session.get("user"))
        self.render("private.html", user_data=user_data)


class PaginationHandler(tornadoweb.TornadoHandler):

    def get(self):
        pag_argument = "pag"
        page = self.get_argument(pag_argument, default=1)
        row_count = 316
        self.render("pagination.html", page=page, row_count=row_count,
                    pag_argument=pag_argument)
