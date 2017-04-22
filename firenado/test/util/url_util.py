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

from __future__ import (absolute_import, division, print_function,
                        with_statement)


import unittest
from firenado.util.url_util import rooted_path

class UrlUtilTestCase(unittest.TestCase):
    """ Case that tests the file util functions.
    """

    def test_root_url_with_slash_in_front_and_back(self):
        """ Happy scenario, root_url with slash back to back
        """
        root_url = "/root/"
        path = "/ext"
        expected = "/root/ext"
        rooted_url = rooted_path(root_url, path)
        self.assertEqual(expected, rooted_url)

    def test_root_url_with_slash_in_front(self):
        """ Happy scenario too, root_url with slash in front
        """
        root_url = "/root"
        path = "/ext"
        expected = "/root/ext"
        rooted_url = rooted_path(root_url, path)
        self.assertEqual(expected, rooted_url)

    def test_root_url_no_slash(self):
        """ root_url with no slash
        """
        root_url = "root"
        path = "/ext"
        expected = "/root/ext"
        rooted_url = rooted_path(root_url, path)
        self.assertEqual(expected, rooted_url)

    def test_root_on_root(self):
        """ root_url pessimistic on root
        """
        root_url = "root/"
        path = "/"
        expected = "/root"
        rooted_url = rooted_path(root_url, path)
        self.assertEqual(expected, rooted_url)
