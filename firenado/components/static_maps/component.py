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

import firenado.tornadoweb
import tornado.web
import os


class StaticMapsComponent(firenado.tornadoweb.TornadoComponent):

    def __init__(self, name, application):
        firenado.tornadoweb.TornadoComponent.__init__(self, name, application)
        self.static_root = None
        self.static_maps = {}

    def get_handlers(self):
        handlers = []
        self.static_root = self.application.get_app_component(
            ).get_component_path()
        if self.conf:
            if 'maps' in self.conf:
                for map in self.conf['maps']:
                    print("Mapping %s items." % map['name'])
                    self.static_maps[map['name']] = {}
                    self.static_maps[map['name']]['root'] = self.static_root
                    if 'root' in map:
                        if os.path.isabs(map['root']):
                            self.static_maps[map['name']]['root'] = map['root']
                        else:
                            self.static_maps[
                                map['name']]['root'] = os.path.abspath(
                                os.path.join(self.static_root, map['root']))
                    if 'items' in map:
                        handlers = handlers + self.get_static_handlers(map)
        return handlers

    def get_static_handlers(self, map):
        static_handlers = []
        for item in map['items']:
            item_path = ""
            if 'path' in item:
                item_path = item['path']
            if 'item_on_path' in item:
                if item['item_on_path']:
                    item_path = os.path.join(item['name'], item_path)
            if 'map_on_path' in item:
                if item['map_on_path']:
                    item_path = os.path.join(map['name'], item_path)
                    print(item_path)
            print("Item  %s items." % map['name'])
            handler = (
                r"%s" % item['handler'],
                tornado.web.StaticFileHandler,
                {"path": os.path.join(
                    self.static_maps[map['name']]['root'],
                    item_path)})
            static_handlers.append(handler)
        return static_handlers

    def get_config_file(self):
        return "static_maps"
