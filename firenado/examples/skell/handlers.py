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

import firenado.tornado


class IndexHandler(firenado.tornado.TornadoHandler):

    def get(self):
        self.render("index.html", message="Hello world!!!")


class SessionHandler(firenado.tornado.TornadoHandler):

    def get(self):
        reset = self.get_argument("reset", False, True)
        if reset:
            self.session.delete('counter')
            self.redirect('/session')
            return None
        counter = 0
        if self.session.has('counter'):
            counter = self.session.get('counter')
        counter += 1
        self.session.set('counter', counter)
        self.render("session.html", session_value=counter)
