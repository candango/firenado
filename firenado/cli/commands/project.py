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
from cartola import fs
import cloup
import firenado.conf
from tornado import template
import os

firenado_section = get_section("firenado")


@cloup.group(aliases=['proj'], cls=FirenadoGroup)
def project():
    """Project related commands"""
    return 0


cli.add_command(project, section=firenado_section)


@project.command()
@cloup.argument('module')
@cloup.option("-s", "--src", is_flag=True)
def init(module: str, src: bool):
    """ Initialize a project """
    # from tornado import template
    component = module.replace(".", " ").title().replace(" ", "")
    project_name = module.lower().split(".")[0]
    project_root = os.path.join(os.getcwd(), project_name)
    module_root = project_root
    if src:
        module_root = os.path.join(module_root, "src")
    if not os.path.isdir(module_root):
        os.makedirs(module_root, exist_ok=True)
    module_target = os.path.join(module_root, module.replace(".", os.sep))
    fs.create_module(module, module_root)
    templates_path = os.path.join(module_target, "templates")
    if not os.path.isdir(templates_path):
        os.mkdir(templates_path)
    # TODO: Check if project exists
    # TODO: If doesn't exists create project
    # TODO: If exists throw an error
    loader = template.Loader(os.path.join(firenado.conf.ROOT,
                                          "cli", "templates",
                                          "project"))
    project_init_content = loader.load("app.py.txt").generate(
        project_name=project_name, module=module, component=component)
    # Generating application firenado component and handlers
    fs.b_write(os.path.join(module_target, "app.py"), project_init_content)
    handlers_file_name = os.path.join(module_target, "handlers.py")
    fs.touch(handlers_file_name)
    project_handlers_content = loader.load("handlers.py.txt").generate(
        handlers=["Index"])
    fs.b_write(handlers_file_name, project_handlers_content)
    # Generating configuration
    project_conf_directory = os.path.join(project_root, "conf")
    # TODO: Handle when the directory exists
    os.mkdir(project_conf_directory)
    project_conf_file = os.path.join(project_conf_directory, "firenado.yml")
    fs.touch(project_conf_file)
    project_init_content = loader.load("firenado.yml.txt").generate(
        app_name=project_name, module=module, component=component)
    fs.b_write(project_conf_file, project_init_content)
    base_html_content = loader.load("base.html.txt").generate()
    base_html_file = os.path.join(templates_path, "base.html")
    fs.b_write(base_html_file, base_html_content)
    index_html_content = loader.load("index.html.txt").generate(
            app_name=project_name)
    index_html_file = os.path.join(templates_path, "index.html")
    fs.b_write(index_html_file, index_html_content)
