# Copyright 2015-2025 Flavio Garcia
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

import cloup
from firenado.cli.root import cli, FirenadoGroup, section


@cloup.group(aliases=['proj'], cls=FirenadoGroup)
def project():
    """Project related commands"""
    return 0


cli.add_command(project, section=section)


@project.command()
@cloup.argument('name')
def init(name: str):
    """Initialize a new Firenado project"""
    print('install', name)
