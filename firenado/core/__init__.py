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

import firenado.conf
from firenado.conf import get_class_from_config
from firenado.core import data
from firenado.core import session
from firenado.core import template
import inspect
import os
from tornado.escape import json_encode
import tornado.web
import logging


class TornadoApplication(tornado.web.Application, data.DataConnectedMixin,
                         session.SessionEnginedMixin):
    """Firenado basic Tornado application.
    """

    def __init__(self, default_host="", transforms=None, **settings):
        logger = logging.getLogger(__name__)
        logger.debug('Wiring application located at %s.' %
                     firenado.conf.APP_ROOT_PATH)
        self.components = {}
        handlers = []
        static_handlers = []
        data.configure_data_sources(firenado.conf.app['data']['sources'], self)
        settings['static_path'] = os.path.join(
            os.path.dirname(__file__), "static")
        self.__load_components()
        for key, component in self.components.iteritems():
            component_handlers = component.get_handlers()
            for i in range(0, len(component_handlers)):
                from firenado.core.websocket import TornadoWebSocketHandler
                if issubclass(
                    component_handlers[i][1], TornadoHandler
                ) or issubclass(
                    component_handlers[i][1], TornadoWebSocketHandler
                ):
                    if len(component_handlers[i]) < 3:
                        component_handlers[i] = (
                            component_handlers[i][0],
                            component_handlers[i][1],
                            {'component': component}
                        )
                    else:
                        component_handlers[i][1].component = component
            handlers = handlers + component_handlers
        if firenado.conf.app['component']:
            settings['static_path'] = os.path.join(self.components[
                firenado.conf.app['component']].get_component_path(), 'static')
        else:
            settings['static_path'] = os.path.join(
                os.path.dirname(__file__), "static")
        tornado.web.Application.__init__(self, handlers=handlers,
                                         default_host=default_host,
                                         transforms=transforms, **settings)

    def __load_components(self):
        """ Loads all enabled components registered into the components
        conf.
        """
        for key, value in firenado.conf.components.iteritems():
            if value['enabled']:
                component_class = get_class_from_config(value)
                self.components[key] = component_class(key, self)
                if self.components[key].get_config_file():
                    comp_config_file = os.path.join(
                        firenado.conf.APP_CONFIG_PATH,
                        self.components[key].get_config_file())
                    if os.path.isfile(comp_config_file):
                        self.components[key].conf = \
                            firenado.conf.load_yaml_config_file(
                                comp_config_file)
                        self.components[key].process_config()
                        self.components[key].initialize()


class TornadoComponent(object):
    """ Firenado applications are organized in components. A component could be
    an application or something that can be distributed as an add-on or a
    plugin.
    """
    def __init__(self, name, application):
        self.name = name
        self.application = application
        self.conf = {}
        self.plugins = dict()

    def get_handlers(self):
        """ Returns handlers being added by the component to the application.
        """
        return []

    def get_component_path(self):
        """ Returns the component path.
        """
        return os.path.abspath(os.path.dirname(
            inspect.getfile(self.__class__)))

    def get_config_file(self):
        return None

    def get_template_path(self):
        """ Returns the path that holds the component's templates.
        """
        return os.path.join(os.path.abspath(os.path.dirname(
            inspect.getfile(self.__class__))), 'templates')

    def initialize(self):
        pass

    def process_config(self):
        """ To process your component configuration please overwrite this
        method reading the data on self.conf.
        """
        pass

    def shutdown(self):
        """ If you have resources that will hang after the shutdown please
        method and close/unload those resources.
        """
        pass

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


#TODO: This is iFlux migration leftover. Is that necessary?.
class JSONError(tornado.web.HTTPError):

    def __init__(self, status_code, log_message=None, *args, **kwargs):
        data = {}
        self.data.update(log_message)
        if not isinstance(log_message, basestring):
            json_log_message = self.data
            json_log_message['code'] = status_code
            json_log_message = json_encode(json_log_message)
        super(JSONError, self).__init__(
            status_code, json_log_message, *args, **kwargs)
