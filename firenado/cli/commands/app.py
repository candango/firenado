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

from ..root import cli, FirenadoGroup
from ..section import get_section
import cloup
import firenado.conf
import sys

firenado_section = get_section("firenado")


@cloup.group(cls=FirenadoGroup)
def app():
    """Application related commands."""
    return 0


cli.add_command(app, section=firenado_section)

app_section = app.section("Sub-commands are")


@app.command(section=app_section)
def install():
    """Triggers all components install methods(to install the app"""
    # TODO: Resolve module if doesn't exists
    if firenado.conf.app['pythonpath']:
        sys.path.append(firenado.conf.app['pythonpath'])
    # TODO This should consider the type of application being handled by
    # Firenado.
    from firenado.tornadoweb import TornadoApplication
    application = TornadoApplication()
    for key, component in application.components.items():
        component.install()


@app.command(section=app_section)
@cloup.option("-a", "--addresses", default=None)
@cloup.option("-A", "--app", default=None)
@cloup.option("-d", "--dir", default=None)
@cloup.option("-p", "--path", default=None)
@cloup.option("-P", "--port", type=int)
@cloup.option("-s", "--socket", default=None)
def run(addresses: str, app: str, dir: str, path: str, port: int,
        socket: str):
    """Runs the application"""
    from firenado.config import get_class_from_config
    """Application related commands."""
    # TODO throw a custom error when type is not found
    # from firenado.config import get_class_from_config
    parameters = {}
    if app is not None:
        parameters['app'] = app
    if dir is not None:
        parameters['dir'] = dir
    if path is not None:
        parameters['path'] = path
    if socket is not None:
        parameters['socket'] = socket
    else:
        if addresses is not None:
            parameters['addresses'] = addresses.split(",")
        if port is not None:
            parameters['port'] = port
    app_type = firenado.conf.app['types'][firenado.conf.app['type']]
    launcher = get_class_from_config(app_type['launcher'])(**parameters)
    launcher.load()
    launcher.launch()
