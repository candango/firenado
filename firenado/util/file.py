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


def write(path, data):
    """ Writes a given data to a file located at the given path. """
    with open(path, 'w') as f:
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
