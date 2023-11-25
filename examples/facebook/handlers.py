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
import tornado
import tornado.auth
import tornado.web


class FacebookHandlerMixin:

    def get_current_user(self):
        user_json = self.session.get("fbdemo_user")
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)


class MainHandler(FacebookHandlerMixin, firenado.tornadoweb.TornadoHandler,
                  tornado.auth.FacebookGraphMixin):

    @firenado.security.authenticated
    @tornado.web.asynchronous
    def get(self):
        self.facebook_request("/me/feed", self._on_stream,
                              access_token=self.current_user["access_token"])

    def _on_stream(self, stream):
        if stream is None:
            # Session may have expired
            self.redirect("/auth/login")
            return
        self.render("stream.html", stream=stream)


class AuthLoginHandler(FacebookHandlerMixin,
                       firenado.tornadoweb.TornadoHandler,
                       tornado.auth.FacebookGraphMixin):

    @tornado.web.asynchronous
    def get(self):
        my_url = (self.request.protocol + "://" + self.request.host +
                  "/auth/login?next=" +
                  tornado.escape.url_escape(self.get_argument("next", "/")))
        if self.get_argument("code", False):
            self.get_authenticated_user(
                redirect_uri=my_url,
                client_id=self.settings["facebook_api_key"],
                client_secret=self.settings["facebook_secret"],
                code=self.get_argument("code"),
                callback=self._on_auth)
            return
        self.authorize_redirect(redirect_uri=my_url,
                                client_id=self.settings["facebook_api_key"],
                                extra_params={"scope": "user_posts"})

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook auth failed")
        self.session.set("fbdemo_user", tornado.escape.json_encode(user))
        self.redirect(self.get_argument("next", "/"))


class AuthLogoutHandler(firenado.tornadoweb.TornadoHandler,
                        tornado.auth.FacebookGraphMixin):

    def get(self):
        self.session.delete("fbdemo_user")
        self.redirect(self.get_argument("next", "/"))
