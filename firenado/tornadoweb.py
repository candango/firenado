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

from __future__ import (absolute_import, division, print_function,
                        with_statement)

import inspect
import logging
import sys

import os
import tornado.httpserver
import tornado.web
import tornado.websocket
from six import iteritems, string_types
from tornado.escape import json_encode

import firenado.conf
from . import session
from .config import get_class_from_config, load_yaml_config_file
from . import data
from . import uimodules
from tornado.template import Loader


logger = logging.getLogger(__name__)


class FirenadoLauncher(object):

    def launch(self):
        return None


class TornadoApplication(tornado.web.Application, data.DataConnectedMixin,
                         session.SessionEnginedMixin):
    """Firenado basic Tornado application.
    """

    def __init__(self, default_host="", transforms=None, **settings):
        logger.debug('Wiring application located at %s.' %
                     firenado.conf.APP_ROOT_PATH)
        self.components = {}
        settings.update(firenado.conf.app['settings'])
        handlers = []
        ui_modules = []
        data.configure_data_sources(firenado.conf.app['data']['sources'], self)
        self.__load_components()
        for key, component in iteritems(self.components):
            component_handlers = component.get_handlers()
            for i in range(0, len(component_handlers)):
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
            # Adding component ui modules to the application ui modules list
            ui_modules.append(uimodules)
            if component.get_ui_modules():
                ui_modules.append(component.get_ui_modules())
        if firenado.conf.app['component']:
            if firenado.conf.app['static_path']:
                if os.path.isabs(firenado.conf.app['static_path']):
                    settings['static_path'] = firenado.conf.app['static_path']
                else:
                    settings['static_path'] = os.path.join(
                            self.components[firenado.conf.app[
                                'component']].get_component_path(),
                            firenado.conf.app['static_path'])
            else:
                settings['static_path'] = os.path.join(
                        self.components[
                            firenado.conf.app[
                                'component']].get_component_path(), 'static')
        else:
            settings['static_path'] = os.path.join(
                    os.path.dirname(__file__), "static")
        static_url_prefix = firenado.conf.app['static_url_prefix']
        if static_url_prefix != "/":
            static_url_prefix = "%s/" % static_url_prefix
        settings['static_url_prefix'] = static_url_prefix
        if len(ui_modules) > 0:
            settings['ui_modules'] = ui_modules
        if firenado.conf.app['cookie_secret']:
            settings['cookie_secret'] = firenado.conf.app['cookie_secret']
        if firenado.conf.app['xsrf_cookies']:
            settings['xsrf_cookies'] = firenado.conf.app['xsrf_cookies']
        if firenado.conf.app['url_root_path'] is not None:
            from .util.url_util import rooted_path
            for idx, handler in enumerate(handlers):
                handler_list = list(handler)
                handler_list[0] = rooted_path(
                    firenado.conf.app['url_root_path'], handler_list[0])
                handlers[idx] = tuple(handler_list)
        tornado.web.Application.__init__(self, handlers=handlers,
                                         default_host=default_host,
                                         transforms=transforms, **settings)
        logger.debug("Checking if session is enabled.")
        if firenado.conf.session['enabled']:
            logger.debug("Session is enabled. Starting session engine.")
            self.session_engine
        else:
            logger.debug("Session is disabled.")

    def get_app_component(self):
        return self.components[firenado.conf.app['component']]

    def __load_components(self):
        """ Loads all enabled components registered into the components
        conf.
        """
        for key, value in iteritems(firenado.conf.components):
            if value['enabled']:
                component_class = get_class_from_config(value)
                self.components[key] = component_class(key, self)
                if self.components[key].get_config_file():
                    from firenado.util.file import file_has_extension
                    filename = self.components[key].get_config_file()
                    comp_config_file = None
                    if file_has_extension(filename):
                        if os.path.isfile(os.path.join(
                                firenado.conf.APP_CONFIG_PATH, filename)):
                            comp_config_file = os.path.join(
                                firenado.conf.APP_CONFIG_PATH, filename)
                    else:
                        config_file_extensions = ['yml', 'yaml']
                        for extension in config_file_extensions:
                            candidate_filename = os.path.join(
                                    firenado.conf.APP_CONFIG_PATH,
                                    '%s.%s' % (filename, extension))
                            if os.path.isfile(candidate_filename):
                                comp_config_file = candidate_filename
                                break
                    if comp_config_file is not None:
                        self.components[key].conf = load_yaml_config_file(
                            comp_config_file)
                        self.components[key].process_config()
                    else:
                        logger.debug('Failed to find the file for the '
                                    'component %s at %s. Component filename '
                                    'returned is %s.' % (
                                        key, firenado.conf.APP_CONFIG_PATH,
                                        self.components[key].get_config_file())
                                    )
                self.components[key].initialize()


class TornadoLauncher(FirenadoLauncher):

    def __init__(self):
        self.http_server = None
        self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = firenado.conf.app[
            'wait_before_shutdown']

    def launch(self):
        import signal

        # TODO: Resolve module if doesn't exists
        if firenado.conf.app['pythonpath']:
            sys.path.append(firenado.conf.app['pythonpath'])

        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        if os.name == "posix":
            signal.signal(signal.SIGTSTP, self.sig_handler)
        self.application = TornadoApplication(debug=firenado.conf.app['debug'])
        self.http_server = tornado.httpserver.HTTPServer(
            self.application)
        if firenado.conf.app['socket']:
            from tornado.netutil import bind_unix_socket
            socket = bind_unix_socket(firenado.conf.app['socket'])
            self.http_server.add_socket(socket)
        else:
            self.http_server.listen(firenado.conf.app['port'])
        tornado.ioloop.IOLoop.instance().start()

    def sig_handler(self, sig, frame):
        logger.warning('Caught signal: %s', sig)
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        import time
        logger.info('Stopping http server')
        for key, component in iteritems(self.application.components):
            component.shutdown()
        self.http_server.stop()

        io_loop = tornado.ioloop.IOLoop.instance()

        if self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN == 0:
            io_loop.stop()
            logger.info('Application is down.')
        else:

            logger.info('Will shutdown in %s seconds ...',
                        self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
            deadline = time.time() + self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or
                                           io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    io_loop.stop()
                    logger.info('Application is down.')
            stop_loop()


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
        :return: A list of handlers the component provides.
        """
        return []

    def get_ui_modules(self):
        """ Returns uimodules the component provides to the application.
        It could be just a module, a list or a dictionary of modules.
        :return: Uimodules the component provides.
        """
        return None

    def get_component_path(self):
        """ Returns the component path.
        """
        return os.path.abspath(os.path.dirname(
            inspect.getfile(self.__class__)))

    def get_config_filename(self):
        return None

    def get_config_file(self):
        filename = self.get_config_filename()
        if filename is not None:
            return filename
        return None

    def get_template_path(self):
        """ Returns the path that holds the component's templates.
        """
        return os.path.join(os.path.abspath(os.path.dirname(
            inspect.getfile(self.__class__))), 'templates')

    def initialize(self):
        """ If you want to add logic while the component is initializing
        please overwrite this method.
        """
        pass

    def install(self):
        """ Firenado handles an application installation looping thought all
        components and triggering the install method of them.
        If
        """
        pass

    def process_config(self):
        """ To process your component configuration please overwrite this
        method reading the data on self.conf.
        """
        pass

    def shutdown(self):
        """ If you have resources that will hang after the shutdown please
        overwrite this method and close/unload those resources.
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

    def is_mobile(self):
        from .util import browser
        if 'User-Agent' in self.request.headers:
            return browser.is_mobile(self.request.headers['User-Agent'])
        return False

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
        for name, variable in iteritems(self.__template_variables):
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

    def get_data_connected(self):
        return self.application

    def get_firenado_template_path(self):
        """Override to customize the firenado template path for each handler.

        By default, we use the ``firenado_template_path`` application setting.
        Return None to load templates relative to the calling file.
        """
        return self.application.settings.get('firenado_template_path')

    def get_rooted_path(self, path):
        from .util.url_util import rooted_path
        root = firenado.conf.app['url_root_path']
        return rooted_path(root, path)

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
        return FirenadoComponentLoader(
            template_path, component=self.component, **kwargs)


class FirenadoComponentLoader(Loader):
    """ A template loader that loads from a single root directory.
    """
    def __init__(self, root_directory, component=None, **kwargs):
        # TODO: Check if we should alter/use the root_directory value
        # here or on the resolve_path method.
        self.component = component
        super(FirenadoComponentLoader, self).__init__(root_directory, **kwargs)

    def resolve_path(self, name, parent_path=None):
        """ When a template name comes with a ':' it means a template from
        another component is being referenced. The component template will be
        resolved and passed to the original Tornado resolve_path method.

        :param name: The template name
        :param parent_path: The template parent path
        :return: Tornado resolve_path result.
        """
        logger.debug("Resolving template %s." % name)
        name_resolved = name
        if ':' in name:
            nameX = name.split(':')
            component_name = nameX[0]
            name_resolved = os.path.join(
                self.component.application.components[
                    component_name].get_template_path(), nameX[-1])
        if name != name_resolved:
            logger.debug("Template %s resolved at %s." % (name, name_resolved))

        return super(FirenadoComponentLoader,
                     self).resolve_path(name_resolved, parent_path)


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
        return FirenadoComponentLoader(
            template_path, component=self.component, **kwargs)


#TODO: This is iFlux migration leftover. Is that necessary?.
class JSONError(tornado.web.HTTPError):

    def __init__(self, status_code, log_message=None, *args, **kwargs):
        data = {}
        self.data.update(log_message)
        if not isinstance(log_message, string_types):
            json_log_message = self.data
            json_log_message['code'] = status_code
            json_log_message = json_encode(json_log_message)
        super(JSONError, self).__init__(
            status_code, json_log_message, *args, **kwargs)
