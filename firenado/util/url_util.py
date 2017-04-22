#!/usr/bin/env python
#
# Copyright 2015-2017 Flavio Garcia
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


def rooted_path(root, path):
    if root is None:
        root = "/"
    if root[0] != "/":
        root = "/%s" % root
    if root[-1] != "/":
        root = "%s/" % root
    rooted_path = "".join([root, path.lstrip("/")])
    if rooted_path == "/":
        return rooted_path
    return rooted_path.rstrip("/")
