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

import os
from tornado.template import Loader


class ComponentLoader(Loader):
    """ A template loader that loads from a single root directory.
    """
    def __init__(self, root_directory, component=None, **kwargs):
        self.component = component
        super(ComponentLoader, self).__init__(root_directory, **kwargs)

    def resolve_path(self, name, parent_path=None):
        """ When a template name comes with a ':' it means a template from
        another component is being referenced. The component template will be
        resolved and passed to the original Tornado resolve_path method.

        :param name: The template name
        :param parent_path: The template parent path
        :return: Tornado resolve_path result.
        """
        if ':' in name:
            nameX = name.split(':')
            component_name = nameX[0]
            name = os.path.join(
                self.component.application.components[
                    component_name].get_template_path(), nameX[-1])
        return super(ComponentLoader, self).resolve_path(name, parent_path)
