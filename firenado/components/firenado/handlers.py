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

import firenado
import firenado.conf
import firenado.tornadoweb
import tornado


class AppInfoHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        self.render(
            "info.html",
            tornado_version=tornado.version,
            firenado=firenado,
            firenado_version=".".join(map(str, firenado.__version__)),
            firenado_conf=firenado.conf,
            handlers=self.application.handlers[0][1],
        )
