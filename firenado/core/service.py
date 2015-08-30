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

import functools
import importlib


class FirenadoService(object):
    """ Base class to handle services. A Firenado service is usually connected to
    an Firenado handler. The developer can add extra configuration using the
    configuration_service method and can get a data source from the
    application using the get_data_source method.
    """

    def __init__(self, handler, data_source = None):
        self.handler = handler
        self.data_source = data_source
        self.configure_service()

    def configure_service(self):
        """ Use this method to add configurations to your service class.
        """
        pass

    def get_data_source(self, name):
        """ Returns a data source by its given name.
        """
        return self.handler.application.data_sources[name]


def served_by(service, attribute_name=None):
    """ Decorator that connects a service to a handler.
    """

    def f_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if isinstance(service, basestring):
                service_x = service.split('.')
                service_module = '.'.join(service_x[:-1])
                service_module = importlib.import_module(
                    '.'.join(service_x[:-1]))
                service_class =  getattr(service_module, service_x[-1])
                service_name = service_x[-1]
            else:
                service_class = service
                service_name = service.__name_
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

