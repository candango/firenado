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

from __future__ import (absolute_import, division, print_function,
                        with_statement)

import functools
import importlib
from six import string_types


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
            if isinstance(service, string_types):
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
            setattr(self, service_attribute, service_class(self))
            return method(self, *args, **kwargs)

        return wrapper
    return f_wrapper
