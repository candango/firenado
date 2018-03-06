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

import os


def create_module(module, target):
    """ Create a module directory structure into the target directory. """
    module_x = module.split('.')
    cur_path = ''
    for path in module_x:
        cur_path = os.path.join(cur_path, path)
        if not os.path.isdir(os.path.join(target, cur_path)):
            os.mkdir(os.path.join(target, cur_path))
        if not os.path.exists(os.path.join(target, cur_path, '__init__.py')):
            touch(os.path.join(target, cur_path, '__init__.py'))
    return cur_path

def file_has_extension(filename):
    """ Return True if the informed filename was extension on it.

    :param filename: The filename.
    :return: True if has extension.
    """
    if get_file_extension(filename) is None:
        return False
    return True


def get_file_extension(filename):
    """ Return the extension if the filename has it. None if not.

    :param filename: The filename.
    :return: Extension or None.
    """
    filename_x = filename.split('.')
    if len(filename_x) > 1:
        if filename_x[-1].strip() is not '':
            return filename_x[-1]
    return None


def write(path, data, binary=False):
    """ Writes a given data to a file located at the given path. """
    mode = "w"
    if binary:
        mode = "wb"
    with open(path, mode) as f:
        f.write(data)
    f.close()


def read(path):
    """ Reads a file located at the given path. """
    data = None
    with open(path, 'r') as f:
        data = f.read()
    f.close()
    return data


def touch(path):
    """ Creates a file located at the given path. """
    with open(path, 'a') as f:
        os.utime(path, None)
    f.close()
