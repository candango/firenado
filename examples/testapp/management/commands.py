#!/usr/bin/env python
#
# Copyright 2015-2021 Flavio Garcia
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

from . import tasks
from firenado.management import ManagementCommand
from tornado import template
import os

TESTAPP_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
loader = template.Loader(os.path.join(TESTAPP_ROOT, "templates", "management"))


ManagementCommand(
    "testapp", "Testapp related commands",
    loader.load("testapp_command_help.txt"), category="Testapp",
    sub_commands=[
        ManagementCommand("command1", "Execute the command 1", "",
                          tasks=tasks.TestAppCommand1Task),
        ManagementCommand("command2", "Execute the command 2", "",
                          tasks=tasks.TestAppCommand2Task)
    ])
