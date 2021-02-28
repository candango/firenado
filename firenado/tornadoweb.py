# -*- coding: UTF-8 -*-
#
# Copyright 2015-2021 Flavio Garcia
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

from cartola import fs
import tornado.web
import firenado.conf
from . import data
from . import session
from . import uimodules
from .config import get_class_from_config, load_yaml_config_file
import inspect
import logging
import os
from six import iteritems
from tornado.httpclient import HTTPRequest
from tornado.template import Loader
import tornado.websocket
from typing import Any

logger = logging.getLogger(__name__)


def get_request(url, **kwargs):
    """ Return a HTTPRequest to help with AsyncHTTPClient and HTTPClient
    execution. The HTTPRequest will use the provided url combined with path
    if provided. The HTTPRequest method will be GET by default and can be
    changed if method is informed.
    If form_urlencoded is defined as True a Content-Type header will be added
    to the request with application/x-www-form-urlencoded value.

    :param str url: Base url to be set to the HTTPRequest
    :key form_urlencoded: If the true will add the header Content-Type
    application/x-www-form-urlencoded to the form. Default is False.
    :key method: Method to be used by the HTTPRequest. Default it GET.
    :key path: If informed will add the path to the base url informed. Default
    is None.
    :return HTTPRequest:
    """
    method = kwargs.get("method", "GET")
    path = kwargs.get("path", None)
    form_urlencoded = kwargs.get("form_urlencoded", False)
    if path is not None:
        if not url.endswith("/"):
            url = "%s/" % url
        url = "%s%s" % (url, path)
    request = HTTPRequest(url, method=method)
    if form_urlencoded:
        request.headers.add("Content-Type",
                            "application/x-www-form-urlencoded")
    return request


class TornadoErrorHandler(object):

    def __init__(self, host):
        self._host = host

    @property
    def host(self):
        return self._host

    def is_component(self):
        if isinstance(self.host, TornadoComponent):
            return True
        return False

    def is_handler(self):
        if isinstance(self.host, TornadoHandler):
            return True
        return False

    def handle_error(self, request: "TornadoHandler", status_code: int,
                     **kwargs: Any) -> None:
        request.write_error(status_code, **kwargs)


class TornadoApplication(tornado.web.Application, data.DataConnectedMixin,
                         session.SessionEnginedMixin):
    """ Firenado basic Tornado application.
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
        """ Loads all enabled components registered from the components
        config section.
        """
        for key, value in iteritems(firenado.conf.components):
            if value['enabled']:
                component_class = get_class_from_config(value)
                self.components[key] = component_class(key, self)
                if self.components[key].get_config_file():
                    filename = self.components[key].get_complete_config_file()
                    if filename is not None:
                        self.components[key].conf = load_yaml_config_file(
                            filename)
                        self.components[key].process_config()
                        self.components[key].has_conf = True
                    else:
                        logger.debug("Failed to find the file for the "
                                     "component %s at %s. Component's "
                                     "filename returned is %s." % (
                                        key, firenado.conf.APP_CONFIG_PATH,
                                        self.components[key].get_config_file())
                                     )
        # Initializing enabled components after the load.
        for key, value in iteritems(firenado.conf.components):
            if value['enabled']:
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
        self._has_conf = False
        self.plugins = dict()

    def after_request(self, handler):
        """ Add a logic to be executed after all component's handlers
        execution.
        """
        pass

    def before_request(self, handler):
        """ Add a logic to be executed before all component's handler
        execution.
        """
        pass

    def get_error_handler(self) -> TornadoErrorHandler:
        """Return a `TornadoErrorHandler` here to provide a different error
        handling than the tornado's default. If the error handler is
        implemented at the component, all handlers will use it as default. If a
        handler implements the `get_error_handler` method, it will be used
        instead of the one implemented at the component."""
        pass

    def is_current_app(self):
        if not firenado.conf.is_multi_app:
            return True
        if firenado.conf.current_app_name == self.name:
            return True
        return False

    @property
    def has_conf(self):
        return self._has_conf

    @has_conf.setter
    def has_conf(self, value):
        self._has_conf = value

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

    def get_complete_config_file(self):
        """ Return the config file with the correct extension, if
        get_config_file has no extension.

        :return str: The config file with extension
        """
        if fs.file_has_extension(self.get_config_file()):
            if os.path.isfile(self.get_config_file()):
                return os.path.join(firenado.conf.APP_CONFIG_PATH,
                                    self.get_config_file())
        config_file_extensions = ['yml', 'yaml']
        for extension in config_file_extensions:
            candidate_filename = "%s.%s" % (self.get_config_file(), extension)
            if os.path.isfile(os.path.join(
                    firenado.conf.APP_CONFIG_PATH, candidate_filename)):
                return os.path.join(firenado.conf.APP_CONFIG_PATH,
                                    candidate_filename)
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
        self.session = None
        self.__template_variables = dict()
        super(TornadoHandler, self).__init__(application, request, **kwargs)

    def initialize(self, component):
        self.component = component

    def add_variable_to_template(self, name, variable):
        """ Add a variable to a dict that will be added to the template during
        the render or render_string execution.
        """
        self.__template_variables[name] = variable

    def authenticated(self):
        """ Returns if the current user is authenticated. If the current user
        is set then we consider authenticated.

        :return: bool True is current user is set
        """
        return self.current_user is not None

    def is_mobile(self):
        from mobiledetect import MobileDetect
        if 'User-Agent' in self.request.headers:
            return MobileDetect(
                useragent=self.request.headers['User-Agent']
            ).is_mobile()
        return False

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        """
        See: https://tinyurl.com/9t3jrend
        :param int status_code:
        :param Any kwargs:
        :return:
        """
        error_handler = self.get_error_handler()
        if error_handler is None:
            error_handler = self.component.get_error_handler()
            if error_handler is None:
                super(TornadoHandler, self).write_error(status_code, **kwargs)
        error_handler.handle_error(self, status_code, **kwargs)


    @session.read
    def prepare(self):
        self.component.before_request(self)
        self.before_request()

    @session.write
    def on_finish(self):
        self.after_request()
        self.component.after_request(self)

    def after_request(self):
        """Called after the end of a request.

        Override this method to perform cleanup, logging, etc.
        This method is a counterpart to `prepare`.  ``on_finish`` may
        not produce any output, as it is called after the response
        has been sent to the client.

        Use this method instead of `on_finish` to avoid the session to break
        and use session features. This method will be called by `on_finish`
        with a valid session.

        This method is called before it's component's after_request if defined.
        """
        pass

    def get_error_handler(self) -> TornadoErrorHandler:
        """Return a `TornadoErrorHandler` here to provide a different error
        handling than the tornado's default. If the error handler is
        implemented at the handler, it will be used instead of the one
        implemented at the component."""
        pass

    def before_request(self):
        """Called at the beginning of a request before  `get`/`post`/etc.

        Override this method to perform common initialization regardless
        of the request method.

        Use this method instead of `prepare` to avoid the session to break and
        use session features. This method will be called by `prepare` with
        a valid session.

        This method is called after it's component's before_request if defined.

        Asynchronous support: Use ``async def`` or decorate this method with
        `.gen.coroutine` to make it asynchronous.
        If this method returns an  ``Awaitable`` execution will not proceed
        until the ``Awaitable`` is done.

        .. versionadded:: 0.1.10
           Asynchronous support.
        """
        pass

    def render_string(self, template_name, **kwargs):
        ignore_component = False
        application_component = None
        for key in ('ignore_component', 'component',):
            if key in kwargs:
                if key == 'ignore_component':
                    ignore_component = kwargs[key]
                if key == 'component':
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


# TODO: We need to create a class to avoid those methods repeated here.
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
        self.component.before_handler(self)

    @session.write
    def on_finish(self):
        self.component.after_handler(self)

    def render_string(self, template_name, **kwargs):
        ignore_component = False
        application_component = None
        for key in ('ignore_component', 'component',):
            if key in kwargs:
                if key == 'ignore_component':
                    ignore_component = kwargs[key]
                if key == 'component':
                    pass
        kwargs['user_agent'] = self.user_agent if hasattr(
            self, 'user_agent') else None
        kwargs['credential'] = self.credential if hasattr(
            self, 'credential') else None
        for name, variable in iteritems(self.__template_variables):
            kwargs[name] = variable
        if self.ui:
            return super(TornadoWebSocketHandler, self).render_string(
                template_name, **kwargs)
        else:
            # TODO: After a redirect I'm still hitting here.
            # Need to figure out what is going on.
            self._finished = False
            return None

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
