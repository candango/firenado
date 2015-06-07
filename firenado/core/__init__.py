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

from __future__ import (absolute_import, division,
                        print_function, with_statement)

import tornado.web


class TornadoApplication(tornado.web.Application):
    """
    Firenado basic Tornado application.
    """

    def __init__(self, handlers=None, default_host="", transforms=None,
                 **settings):
        self.components = {}

        composed_handlers = handlers

        tornado.web.Application.__init__(self, composed_handlers, default_host,
                                         transforms, **settings)
