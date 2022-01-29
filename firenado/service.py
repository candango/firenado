# -*- coding: UTF-8 -*-
#
# Copyright 2015-2022 Flávio Gonçalves Garcia
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

import functools
import importlib
import inspect
import logging

logger = logging.getLogger(__name__)


class FirenadoService(object):
    """ Base class to handle services. A Firenado service is usually connected
    to a handler or a service.
    The developer can add extra configuration using the configuration_service
    method and can get a data source from the data connected instance using
    either get_data_sources or get_data_source methods.
    """

    def __init__(self, consumer, data_source=None):
        self.consumer = consumer
        self.data_source = data_source
        self.configure_service()

    def configure_service(self):
        """ Use this method to add configurations to your service class.
        """
        pass

    def get_data_source(self, name):
        """ Returns a data source by its given name.
        """
        return self.get_data_sources()[name]

    def get_data_sources(self):
        """ If a data connected is returned then returns all data sources.
        If not returns None.

        :return: The data connected data sources
        """
        data_connected = self.data_connected
        if data_connected is not None:
            return data_connected.data_sources
        return None

    @property
    def data_connected(self):
        """ Will recurse over services until the data connected instance.
        If service has no consumer returns None.

        :return: The data connected object in the top of the hierarchy.
        """
        if self.consumer is None:
            return None
        from firenado.data import DataConnectedMixin
        if isinstance(self.consumer, DataConnectedMixin):
            return self.consumer
        invert_op = getattr(self.consumer, "get_data_connected", None)
        if callable(invert_op):
            return self.consumer.get_data_connected()
        return self.consumer.data_connected


def served_by(service, attribute_name=None):
    """ Decorator that connects a service to a service consumer.
    """

    def f_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if isinstance(service, str):
                service_x = service.split('.')
                service_module = importlib.import_module(
                    '.'.join(service_x[:-1]))
                service_class = getattr(service_module, service_x[-1])
                service_name = service_x[-1]
            else:
                service_class = service
                service_name = service.__name__
            service_attribute = ''
            if attribute_name is None:
                first = True
                for s in service_name:
                    if s.isupper():
                        if first:
                            service_attribute = ''.join([
                                service_attribute, s.lower()])
                        else:
                            service_attribute = ''.join([
                                service_attribute, '_', s.lower()])
                    else:
                        service_attribute = ''.join([service_attribute, s])
                    first = False
            else:
                service_attribute = attribute_name
            must_set_service = False
            if not hasattr(self, service_attribute):
                must_set_service = True
            else:
                if getattr(self, service_attribute) is None:
                    must_set_service = True
            if must_set_service:
                setattr(self, service_attribute, service_class(self))
            return method(self, *args, **kwargs)

        return wrapper
    return f_wrapper


def sessionned(*args, **kwargs):
    """ This decorator will add an existing session to the method being
    decorated or create a new session to be used by the method."""
    service = None
    if len(args) > 0:
        service = args[0]

    def method_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *method_args, **method_kwargs):
            session = method_kwargs.get("session")
            close = kwargs.get("close", False)
            close = method_kwargs.get("close", close)
            if not session:
                data_source = kwargs.get("data_source")
                data_source = method_kwargs.get("data_source", data_source)
                if not data_source:
                    hasattr(self, "default_data_source")
                    if hasattr(self, "default_data_source"):
                        if inspect.ismethod(self.default_data_source):
                            data_source = self.default_data_source()
                        else:
                            data_source = self.default_data_source
                try:
                    if isinstance(data_source, str):
                        ds = self.get_data_source(data_source)
                        method_kwargs['data_source'] = data_source
                        session = ds.session
                    else:
                        print(data_source)
                        session = data_source.session
                    method_kwargs['session'] = session
                except KeyError:
                    logger.exception("There is no datasource defined with"
                                     "index \"%s\" related to the service." %
                                     data_source)
            result = method(self, *method_args, **method_kwargs)
            if close:
                if not session:
                    logger.warning("No session was resolved.")
                logger.debug("Closing session %s." % session)
                session.close()
            return result
        return wrapper
    # If the decorator has no parameter, I mean no parentesis, we need to wrap
    # the service variable again , instead of the service instance, we need to
    # deal with the method being decorated but as a <function> instace.
    if inspect.isfunction(service):
        @functools.wraps(None)
        def func_wrapper(_function):
            return method_wrapper(_function)
        return func_wrapper(service)
    return method_wrapper
