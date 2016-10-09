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

import facebook.handlers
import firenado.tornadoweb
import tornado


class FacebookComponent(firenado.tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', facebook.handlers.MainHandler),
            (r"/auth/login", facebook.handlers.AuthLoginHandler),
            (r"/auth/logout", facebook.handlers.AuthLogoutHandler),
        ]

    def get_ui_modules(self):
        return {"Post": PostModule}


class PostModule(tornado.web.UIModule):
    def render(self, post):
        return self.render_string("modules/post.html", post=post)
