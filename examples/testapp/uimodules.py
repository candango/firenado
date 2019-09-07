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

import tornado.web


class Header1(tornado.web.UIModule):

    def render(self, header):
        return self.render_string('header1.html', header=header)


class LoginErrorMessage(tornado.web.UIModule):

    def render(self, key):

        if self.handler.session.has('login_errors'):
            errors = self.handler.session.get('login_errors')
            if key in errors:
                template = "testapp:uimodules/login_error_message.html"
                return self.render_string(template, message=errors[key])
        return ""
