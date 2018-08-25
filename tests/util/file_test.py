#!/usr/bin/env python
#
# Copyright 2015-2018 Flavio Garcia
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
from firenado.util.file import file_has_extension, get_file_extension


class FileTestCase(unittest.TestCase):
    """ Case that tests the file util functions.
    """

    def test_extension_file_with_extension(self):
        """ Happy scenario, a filename with an extension
        """
        filename = 'the_file.ext'
        expected_extension = 'ext'
        extension = get_file_extension(filename)
        self.assertEqual(extension, expected_extension)
        self.assertTrue(file_has_extension(filename))

    def test_extension_file_ending_with_dot(self):
        """ Filename ending with a dot
        """
        filename = 'the_file.'
        extension = get_file_extension(filename)
        self.assertIsNone(extension)
        self.assertFalse(file_has_extension(filename))

    def test_extension_file_no_extension(self):
        """ Filename without extension
        """
        filename = 'the_file'
        extension = get_file_extension(filename)
        self.assertIsNone(extension)
        self.assertFalse(file_has_extension(filename))
