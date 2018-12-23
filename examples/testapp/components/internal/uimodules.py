#!/usr/bin/env python
#
# Copyright 2015-2016 Flavio Garcia
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

import tornado.web


class Header2(tornado.web.UIModule):

    def render(self, header):
        """ On this ui module example it is tested a second ui module package
        insertion to the application ui modules stack and, rendering a template
        from another component while rendering the ui module.

        :param header: The header string to be rendered by the module.
        :return: A header string
        """
        return self.render_string('testapp:header2.html', header=header)
