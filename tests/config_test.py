#!/usr/bin/env python
#
# Copyright 2015-2019 Flavio Garcia
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

import unittest
from firenado.config import (get_class_from_config, get_class_from_module,
                             get_class_from_name)
from firenado.session import SessionEngine


class GetClassTestCase(unittest.TestCase):
    """ Case that test all get class functions.
    """

    def test_get_class_from_config(self):
        """ Getting classes from configs."""
        default_config = {"module": "firenado.session",
                          "class": "SessionEngine"}

        custom_config = {"module": "firenado.session",
                         "my_class": "SessionEngine"}

        result = get_class_from_config(default_config)
        result_custom = get_class_from_config(custom_config, index="my_class")

        self.assertTrue(result == SessionEngine)
        self.assertTrue(result_custom == SessionEngine)

    def test_get_class_from_name(self):
        """ Getting a class from the full class name."""
        result = get_class_from_name("firenado.session.SessionEngine")
        self.assertTrue(result == SessionEngine)

    def test_get_class_from_module(self):
        """ Getting a class from a given module and class name parameters. """
        result = get_class_from_module("firenado.session", "SessionEngine")
        self.assertTrue(result == SessionEngine)
