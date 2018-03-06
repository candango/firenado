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

import firenado.conf
import firenado.tornadoweb
from firenado import service
from firenado.components.toolbox.pagination import Paginator
from firenado.security import authenticated


class AuthenticatedHandler(firenado.tornadoweb.TornadoHandler):

    def get_current_user(self):
        from tornado.escape import json_decode
        user_cookie = self.session.get("user")
        if user_cookie:
            return json_decode(user_cookie)
        return None


class IndexHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        import firenado.conf
        default_login = firenado.conf.app['login']['urls']['default']
        self.render("index.html", message="Hello world!!!",
                    login_url=default_login)


class SessionTimeoutHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        self.render("session_timeout.html",
                    session_conf=firenado.conf.session)


class SessionCounterHandler(firenado.tornadoweb.TornadoHandler):

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


class LoginHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        default_login = firenado.conf.app['login']['urls']['default']
        errors = {}
        if self.session.has('login_errors'):
            errors = self.session.get('login_errors')
        self.render("login.html", errors=errors,
                    login_url=default_login)

    @service.served_by("skell.services.LoginService")
    @service.served_by("skell.services.UserService")
    def post(self):
        from tornado.escape import json_encode
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
                self.session.set("user", json_encode(user))
                self.redirect(self.get_rooted_path("private"))

        if errors:
            self.session.set('login_errors', errors)
            self.redirect(self.get_rooted_path(default_login))


class PrivateHandler(AuthenticatedHandler):

    @authenticated
    def get(self):
        self.render("private.html")


class PaginationHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        pag_argument = "pag"
        page = self.get_argument(pag_argument, default=1)
        row_count = 316
        paginator = Paginator(row_count, page)
        self.render("pagination.html", row_count=row_count, page=page,
                    paginator=paginator, pag_argument=pag_argument)
