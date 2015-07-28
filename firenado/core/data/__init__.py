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
import types

def configure_data_sources(data_sources, data_connected):
    """
    Configures data sources to a data connected object.
    :param data_sources: List of data sources to be configured
    :param data_connected: Data connected object where the data sources will
    be configured.
    """
    data_connected_class = "%s.%s" % (data_connected.__module__, 
        data_connected.__class__.__name__)
    if isinstance(data_sources, types.StringTypes):
        import firenado.conf
        # TODO Handler unknow connection instance here
        config = firenado.conf.data['sources'][data_sources]
        connection_handler_config = firenado.conf.data['connectors'][
            config['connector']]
        module = importlib.import_module(connection_handler_config['module'])
        handler_class = getattr(module, connection_handler_config['class'])
        data_source_instance = handler_class(data_connected)
        config = data_source_instance.process_config(config)
        data_source_instance.configure(config)
        data_connected.set_data_source(data_sources, data_source_instance)
        # Testing the connection
        # Without that the error will just happen during the handler execution
    elif isinstance(data_sources, list):
        for data_source in data_sources:
            configure_data_sources(data_source, data_connected)
    #TODO Throw an error here if it is not string or list
        

def configure(data_sources):
    """ Decorator that configures data sources on a data connected object.
    :param data_sources: List of data sources to be configured.
    """
    def f_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            configure_data_sources(data_sources, self)
            return method(self, *args, **kwargs)
        return wrapper
    return f_wrapper


class DataConnectedMixin(object):
    """ Data connected objects has data sources. This mixin prepares an
    object to to have data sources set to it and retrieved from it.

    Example:
    >>> class MyClass(..., DataConnectedMixin):
    """

    @property
    def data_sources(self):
        """ Returns all connectors registered to the data connected instance.
        """
        return get_data_sources(self, '__data_sources')

    def get_data_source(self, id):
        """ Returns a connector by it's id.
        """
        return self.data_sources[id]

    def set_data_source(self, id, data_source):
        """ Add a connector to the connectors collection.
        """
        self.data_sources[id] = data_source


def get_data_sources(obj, data_sources_attribute):
    if not hasattr(obj, data_sources_attribute):
        setattr(obj, data_sources_attribute, {})
    return getattr(obj, data_sources_attribute)
