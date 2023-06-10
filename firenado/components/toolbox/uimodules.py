# Copyright 2015-2023 Flavio Garcia
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

from cartola.pagination import Paginator
import tornado.web


class Paginate(tornado.web.UIModule):

    def render(self, count, **kwargs):
        name = kwargs.get("name", "paginator")
        template = kwargs.get("template", "toolbox:uimodules/pagination.html")
        parameters = {}
        component_conf = self.handler.component.conf
        per_page = 10
        per_block = 10
        if 'pagination' in component_conf:
            if 'per_page' in component_conf['pagination']:
                per_page = component_conf['pagination']['per_page']
            if 'per_block' in component_conf['pagination']:
                per_block = component_conf['pagination']['per_block']

        argument = kwargs.get("argument", "p")
        page = self.request.arguments.get(argument, kwargs.get("page"))
        if isinstance(page, list):
            page = self.request.arguments.get(argument)[0]
        if page:
            page = int(page)
        if page:
            parameters['page'] = page

        parameters['per_page'] = kwargs.get("per_page", per_page)
        parameters['per_block'] = kwargs.get("per_block", per_block)
        paginator = Paginator(count, **parameters)
        setattr(self.handler, name, paginator)
        return self.render_string(template, argument=argument,
                                  paginator=paginator)
