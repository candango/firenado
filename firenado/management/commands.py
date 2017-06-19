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

import firenado.conf
from firenado.management import ManagementCommand
from firenado.management import tasks
from tornado import template
import os

loader = template.Loader(os.path.join(firenado.conf.ROOT,
                                      "management", "templates", "help"))
ManagementCommand(
    'app', 'Application related commands', loader.load("app_command_help.txt"),
    category='Firenado',
    sub_commands=[
        ManagementCommand('install', 'Install a Firenado application', "",
                          tasks=tasks.InstallProjectTask),
        ManagementCommand('run', 'Runs a Firenado application', '',
                          tasks=tasks.RunApplicationTask),
        ManagementCommand("cookie_secret_gen",
                          "Generates a random cookie secret", "",
                          tasks=tasks.GenerateCookieSecretTask),
    ])
ManagementCommand(
    'proj(ect)', 'Project related commands',
    loader.load("project_command_help.txt"), category='Firenado',
    sub_commands=[
        ManagementCommand('init', 'Initiates a new Firenado project', '',
                          tasks=tasks.CreateProjectTask)
    ])
