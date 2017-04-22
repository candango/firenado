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

import tornado.web
from .pagination import Paginator


class Paginate(tornado.web.UIModule):

    def render(self, row_count, current_page, rows_per_page=None,
               pages_per_block=None, argument="p",
               template="toolbox:uimodules/pagination.html"):
        component_conf = self.handler.component.conf
        if 'pagination' in self.handler.component.conf:
            if 'rows_per_page' in component_conf['pagination']:
                rows_per_page = component_conf['pagination']['rows_per_page']
            if 'pages_per_block' in component_conf['pagination']:
                pages_per_block = component_conf['pagination'][
                    'pages_per_block']
        if rows_per_page is None:
            rows_per_page = 10
        if pages_per_block is None:
            pages_per_block = 10
        paginator = Paginator(row_count, current_page, rows_per_page,
                              pages_per_block)
        return self.render_string(template,argument=argument,
                                  paginator=paginator)
