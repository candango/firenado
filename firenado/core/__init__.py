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
import inspect
import os
from tornado.escape import json_encode
import tornado.web


class TornadoApplication(tornado.web.Application):
    """Firenado basic Tornado application.
    """

    def __init__(self, handlers=None, default_host="", transforms=None,
                 **settings):
        self.components = {}

        composed_handlers = handlers

        tornado.web.Application.__init__(self, composed_handlers, default_host,
                                         transforms, **settings)


class TornadoComponent(object):
    """Firenado applications are organized in components. A component could be
    the proper application or something that can be distributed as an add-on or
    a plugin.
    """

    def __init__(self, name, application, config={}):
        self.name = name
        self.application = application
        self.config = config
        self.plugins = dict()

    def get_handlers(self):
        """Return handlers being added by the component to the application.
        """
        return []

    def get_component_path(self):
        """Return the component path.
        """
        return os.path.dirname(inspect.getfile(self.__class__))

    def get_template_path(self):
        """Return the path that holds the component's templates.
        """
        return os.path.join(os.path.dirname(
            inspect.getfile(self.__class__)), 'templates')


class TornadoHandler(tornado.web.RequestHandler):
    """ Base request handler to be used on a Firenado application.
    It provides session and handles component paths.
    """

    def __init__(self, application, request, **kwargs):
        self.component = None
        self.__template_variables = dict()
        super(TornadoHandler, self).__init__(application, request, **kwargs)

    def initialize(self, component):
        self.component = component

    def add_variable_to_template(self, name, variable):
        """ Add a variable to a dict that will be added to the template during
        the render or render_string execution.
        """
        self.__template_variables[name] = variable

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
            return super(TornadoHandler, self).render_string(
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
            return super(TornadoHandler, self).get_template_path()
        else:
            return self.component.get_template_path()


#TODO: This is iFlux migration leftover. Need to figure out we should keep
# that.
class JSONError(tornado.web.HTTPError):

    data = {}

    def __init__(self, status_code, log_message=None, *args, **kwargs):
        self.data.update(log_message)
        if not isinstance(log_message, basestring):
            json_log_message = self.data
            json_log_message['code'] = status_code
            json_log_message = json_encode(json_log_message)
        super(JSONError, self).__init__(
            status_code, json_log_message, *args, **kwargs)

