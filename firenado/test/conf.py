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

from __future__ import (absolute_import, division, print_function,
                        with_statement)

from firenado.core import TornadoApplication, TornadoHandler, TornadoComponent
import unittest
import firenado.conf
import six

reload = None
if six.PY2:
    reload = reload
elif six.PY34:
    import importlib
    reload = importlib.reload


class ApplicationComponentTestCase(unittest.TestCase):
    """ Case that tests an Firenado application after being loaded from its
    configuration file.
    """

    def test_only_framework_stack(self):

        reload(firenado.conf)
        self.assertEquals(firenado.conf.stack[0],
                          firenado.conf.LIB_CONFIG_FILE)
