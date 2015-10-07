#!/usr/bin/env python
#
# Copyright 2015 Flavio Garcia
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
#
# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:

import firenado.core
import tornado.web
import os


class AssetsComponent(firenado.core.TornadoComponent):

    def get_handlers(self):
        handlers = []
        if self.conf:
            if 'bower' in self.conf:
                handlers = handlers + self.get_bower_handlers(
                    self.conf['bower'])
        return handlers

    def get_bower_handlers(self, bower_conf):
        bower_handlers = []
        if 'dependencies' in bower_conf:
            for dependency in bower_conf['dependencies']:
                handler = (
                    r"%s" % dependency['handler'],
                    tornado.web.StaticFileHandler,
                    {"path": os.path.join(
                        self.application.get_app_component(
                        ).get_component_path(),
                        'bower_components',
                        dependency['path'])})
                bower_handlers.append(handler)
        return bower_handlers

    def get_config_file(self):
        return "assets.yaml"
