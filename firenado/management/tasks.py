# -*- coding: UTF-8 -*-
#
# Copyright 2015-2020 Flavio Garcia
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

from cartola import fs
import firenado.conf
from firenado.management import ManagementTask
from firenado.util import argparse_util
import logging
import os
from six import iteritems
import sys

logger = logging.getLogger(__name__)


class CreateProjectTask(ManagementTask):
    """
    Creates a new project from scratch
    """
    def run(self, namespace):
        from tornado import template
        if len(sys.argv) > 2:
            module = namespace.module
            component = module.replace(".", " ").title().replace(" ", "")
            project_name = module.replace(".", "_").lower()
            project_directory = fs.create_module(module, os.getcwd())
            #TODO: Check if project exists
            #TODO: If doesn't exists create project
            #TODO: If exists throw an error
            loader = template.Loader(os.path.join(firenado.conf.ROOT,
                                                  "management", "templates",
                                                  "project"))
            project_init_content = loader.load("app.py.txt").generate(
                project_name=project_name, module=module, component=component)
            # Generating application firenado component and handlers
            fs.write(os.path.join(project_directory, "__init__.py"), "")
            fs.write(os.path.join(project_directory, "app.py"),
                        project_init_content.decode(sys.stdout.encoding))
            handlers_file_name = os.path.join(project_directory, "handlers.py")
            fs.touch(handlers_file_name)
            project_handlers_content = loader.load("handlers.py.txt").generate(
                handlers=["Index"])
            fs.write(handlers_file_name,
                        project_handlers_content.decode(sys.stdout.encoding))
            # Generating configuration
            project_conf_directory = os.path.join(project_directory, "conf")
            os.mkdir(project_conf_directory)
            project_conf_file = os.path.join(project_conf_directory,
                                             "firenado.yml")
            fs.touch(project_conf_file)
            project_init_content = loader.load("firenado.yml.txt").generate(
                app_name=project_name, module=module, component=component)
            fs.write(project_conf_file,
                        project_init_content.decode(sys.stdout.encoding))
        else:
            #TODO: This thing has to go. The parameter validation should be
            #TODO: executed by the argument parser.
            loader = template.Loader(os.path.join(
                firenado.conf.ROOT, "management", "templates", "help"))
            help_message = loader.load("init_command_help.txt").generate()

    def add_arguments(self, parser):
        """
        Add module argument to the command parser.

        :param parser: The current parser validating the command holding this
        task.
        """
        parser.add_argument("module", help="The project module")

    def get_error_message(self, parser, exception):
        """

        :param parser:
        :param argparse_util.FirenadoArgumentError exception:
        :return:
        """
        return str(exception)


class InstallProjectTask(ManagementTask):
    """ Triggers the install method of all components registered in the
    application.
    """
    def run(self, namespace):
        # TODO: Resolve module if doesn't exists
        if firenado.conf.app['pythonpath']:
            sys.path.append(firenado.conf.app['pythonpath'])
        # TODO This should consider the type of application being handled by
        # Firenado.
        from firenado.tornadoweb import TornadoApplication
        application = TornadoApplication()
        for key, component in iteritems(application.components):
            component.install()


class RunApplicationTask(ManagementTask):

    def add_arguments(self, parser):
        parser.add_argument("-a", "--addresses", default=None)
        parser.add_argument("-A", "--app", default=None)
        parser.add_argument("-d", "--dir", default=None)
        parser.add_argument("-p", "--path", default=None)
        parser.add_argument("-P", "--port", type=int)
        parser.add_argument("-s", "--socket", default=None)

    """ Runs a Firenado Tornado Application based
    on the it's project configuration
    """
    def run(self, namespace):
        #TODO throw a custom error when type is not found
        from firenado.config import get_class_from_config
        parameters = {}
        if namespace.app is not None:
            parameters['app'] = namespace.app
        if namespace.dir is not None:
            parameters['dir'] = namespace.dir
        if namespace.path is not None:
            parameters['path'] = namespace.path
        if namespace.socket is None:
            if namespace.addresses is not None:
                parameters['addresses'] = namespace.addresses.split(",")
            if namespace.port is not None:
                parameters['port'] = namespace.port
        else:
            parameters['socket'] = namespace.socket
        app_type = firenado.conf.app['types'][firenado.conf.app['type']]
        launcher = get_class_from_config(app_type['launcher'])(**parameters)
        launcher.load()
        launcher.launch()


class GenerateRandomStringTask(ManagementTask):
    """ Generates a random string to serve as the cookie secret for an
    application.
    """

    def add_arguments(self, parser):
        parser.add_argument("size", nargs='?', default=64, type=int)

    def run(self, namespace):
        from cartola import security
        size = namespace.size
        if size > 1000000:
            logger.error("The size {} has reached this command "
                         "limit.".format(size))
            sys.exit(1)
        logger.debug("Displaying a random string with size {}".format(size))
        print(security.random_string(size))
        sys.exit(0)


class GenerateUuidTask(ManagementTask):
    """ Generates an uuid4 string
    """
    def run(self, namespace):
        from uuid import uuid4
        logger.debug("Displaying a random uuid4 string.")
        print(uuid4())
        sys.exit(0)
