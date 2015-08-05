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

from __future__ import (absolute_import, division,
                        print_function, with_statement)

from firenado.core import JSONError
from firenado.core import session
from firenado.core import template
import tornado.websocket


# TODO: We need to create a class to avoid those methods repetition here.
class TornadoWebSocketHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        self.component = None
        self.__template_variables = dict()
        super(TornadoWebSocketHandler, self).__init__(application,
                                                      request, **kwargs)

    def initialize(self, component):
        self.component = component

    def add_variable_to_template(self, name, variable):
        """ Add a variable to a dict that will be added to the template during
        the render or render_string execution.
        """
        self.__template_variables[name] = variable

    @session.read
    def prepare(self):
        pass
        #self.component.run_before_handler(self)

    @session.write
    def on_finish(self):
        pass
        #self.component.run_after_handler(self)

    def render_string(self, template_name, **kwargs):
        ignore_component = False
        application_component = None
        for key in ('ignore_component', 'component',):
            if key in kwargs:
                if key is 'ignore_component':
                    ignore_component = kwargs[key]
                if key is 'component':
                   pass
        kwargs['user_agent'] = self.user_agent if hasattr(
            self, 'user_agent') else None
        kwargs['credential'] = self.credential if hasattr(
            self, 'credential') else None
        for name, variable in self.__template_variables.iteritems():
            kwargs[name] = variable
        if self.ui:
            return super(TornadoWebSocketHandler, self).render_string(
                template_name, **kwargs)
        else:
            # TODO: After a redirect I'm still hitting here.
            # Need to figure out what is going on.
            self._finished = False
            return None

    def write_error(self, status_code, **kwargs):
        error_stack = {'code': status_code}

        exc_info = None
        for key in kwargs:
            if key == 'exc_info':
                exc_info = kwargs[key]
        error = exc_info[1]

        if type(error) == JSONError:
            error_stack.update(error.data)
            response = dict(data=None, error=error_stack)
            self.write(response)
        else:
            raise error

    def get_firenado_template_path(self):
        """Override to customize the firenado template path for each handler.

        By default, we use the ``firenado_template_path`` application setting.
        Return None to load templates relative to the calling file.
        """
        return self.application.settings.get('firenado_template_path')

    def get_template_path(self):
        """Override to customize template path for each handler.

        By default, we use the ``template_path`` application setting.
        Return None to load templates relative to the calling file.
        """
        if self.component is None:
            # This is the default behaviour provided by Tornado.
            # No components on the request no fancy template path.
            return super(TornadoWebSocketHandler, self).get_template_path()
        else:
            return self.component.get_template_path()

    def create_template_loader(self, template_path):
        """Returns a new template loader for the given path.

        May be overridden by subclasses.  By default returns a
        directory-based loader on the given path, using the
        ``autoescape`` application setting.  If a ``template_loader``
        application setting is supplied, uses that instead.
        """
        settings = self.application.settings
        kwargs = {}
        if 'autoescape' in settings:
            # autoescape=None means "no escaping", so we have to be sure
            # to only pass this kwarg if the user asked for it.
            kwargs['autoescape'] = settings['autoescape']
        return template.ComponentLoader(
            template_path, component=self.component, **kwargs)
