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

import firenado.security
import firenado.tornadoweb

from tornado.auth import GoogleOAuth2Mixin
from tornado.escape import json_decode, json_encode

from tornado import gen


class GoogleHandlerMixin:

    COOKIE_NAME = 'googledemo_user'

    def get_current_user(self):
        user_json = self.session.get(self.COOKIE_NAME)
        print(user_json)
        if not user_json:
            return None
        return json_decode(user_json)


class MainHandler(GoogleHandlerMixin, firenado.tornadoweb.TornadoHandler,
                  GoogleOAuth2Mixin):

    @firenado.security.authenticated
    @gen.coroutine
    def get(self):
        self.write(self.get_current_user())


class LoginHandler(GoogleHandlerMixin, firenado.tornadoweb.TornadoHandler,
                   GoogleOAuth2Mixin):
    @gen.coroutine
    def get(self):
        my_redirect_url = "%s://%s/login" % (self.request.protocol,
                                              self.request.host)
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=my_redirect_url,
                code=self.get_argument('code'))
            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            # Save the user and access token with
            # e.g. set_secure_cookie.
            self.session.set(self.COOKIE_NAME, json_encode(user))
            self.redirect(self.get_argument('next', '/'))
        else:
            yield self.authorize_redirect(
                redirect_uri=my_redirect_url,
                client_id=self.settings['google_oauth']['key'],
                client_secret=self.settings['google_oauth']['secret'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class LogoutHandler(GoogleHandlerMixin, firenado.tornadoweb.TornadoHandler):

    def get(self):
        self.session.delete(self.COOKIE_NAME)
