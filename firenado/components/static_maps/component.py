#!/usr/bin/env python
#
# Copyright 2015-2018 Flavio Garcia
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
import logging
import tornado.web
import os

logger = logging.getLogger(__name__)


class StaticMapsComponent(firenado.tornadoweb.TornadoComponent):
    """ The static maps component helps to map static handlers using a config
    file.
    """

    def __init__(self, name, application):
        firenado.tornadoweb.TornadoComponent.__init__(self, name, application)
        self.static_root = None
        self.static_maps = {}

    def get_handlers(self):
        """ Returns the handlers defined on the static_maps.yml file located
        at the app config directory.

        Returns: An array of static handlers to be added to the app.
        """
        handlers = []
        self.static_root = self.application.get_app_component(
        ).get_component_path()
        if self.conf:
            if 'maps' in self.conf:
                if self.conf['maps'] is None:
                    logger.warning("Maps configuration is empty. Finish the"
                                   "static maps configuration.")
                    return handlers
                for map_item in self.conf['maps']:
                    logger.debug("Mapping %s handlers." % map_item['name'])
                    self.static_maps[map_item['name']] = {}
                    self.static_maps[
                        map_item['name']]['root'] = self.static_root
                    if 'root' in map_item:
                        if os.path.isabs(map_item['root']):
                            self.static_maps[
                                map_item['name']]['root'] = map_item['root']
                        else:
                            self.static_maps[
                                map_item['name']]['root'] = os.path.abspath(
                                os.path.join(self.static_root,
                                             map_item['root']))
                    if 'handlers' in map_item:
                        if map_item['handlers'] is None:
                            logger.warning("There is no handles mapped in the"
                                           " static maps config file.")
                        else:
                            handlers = handlers + self.get_static_handlers(
                                map_item)
        else:
            logger.warning("No static maps configurations were provided.")
        return handlers

    def get_static_handlers(self, map_item):
        static_handlers = []
        for handler in map_item['handlers']:
            handler_path = ""
            if 'path' in handler:
                handler_path = handler['path']
            if 'name_on_path' in handler:
                if handler['name_on_path']:
                    handler_path = os.path.join(handler['name'], handler_path)
            if 'map_on_path' in handler:
                if handler['map_on_path']:
                    handler_path = os.path.join(map_item['name'], handler_path)
            logger.debug(
                "Mapping handler %s on directory %s on the map %s." % (
                    handler['handler'], handler_path, map_item['name']))
            static_handler = (
                r"%s" % handler['handler'],
                tornado.web.StaticFileHandler,
                {"path": os.path.join(
                    self.static_maps[map_item['name']]['root'],
                    handler_path)})
            static_handlers.append(static_handler)
        return static_handlers

    def get_config_file(self):
        return "static_maps"
