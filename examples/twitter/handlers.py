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

from tornado.auth import TwitterMixin
from tornado.escape import json_decode, json_encode

from tornado import gen


class TwitterHandlerMixin:

    COOKIE_NAME = 'twitterdemo_user'

    def get_current_user(self):
        user_json = self.session.get(self.COOKIE_NAME)
        print(user_json)
        if not user_json:
            return None
        return json_decode(user_json)


class MainHandler(TwitterHandlerMixin, firenado.tornadoweb.TornadoHandler, TwitterMixin):

    @firenado.security.authenticated
    @gen.coroutine
    def get(self):
        timeline = yield self.twitter_request(
            '/statuses/home_timeline',
            access_token=self.current_user['access_token'])
        self.render('home.html', timeline=timeline)


class LoginHandler(TwitterHandlerMixin, firenado.tornadoweb.TornadoHandler, TwitterMixin):
    @gen.coroutine
    def get(self):
        if self.get_argument('oauth_token', None):
            user = yield self.get_authenticated_user()
            del user["description"]
            self.session.set(self.COOKIE_NAME, json_encode(user))
            self.redirect(self.get_argument('next', '/'))
        else:
            yield self.authorize_redirect(callback_uri=self.request.full_url())


class LogoutHandler(TwitterHandlerMixin, firenado.tornadoweb.TornadoHandler):

    def get(self):
        self.session.delete(self.COOKIE_NAME)
