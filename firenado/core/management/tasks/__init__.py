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

import firenado.conf
from firenado.core.management import ManagementTask
from firenado.util import file as _file

import logging
import tornado.ioloop
import tornado.httpserver

import os
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
            component = module.replace('.', ' ').title().replace(' ', '')
            project_name = module.replace('.', '_').lower()
            project_directory = _file.create_module(module, os.getcwd())
            #TODO: Check if project exists
            #TODO: If doesn't exists create project
            #TODO: If exists throw an error
            loader = template.Loader(os.path.join(firenado.conf.ROOT,
                                                  'core', 'management',
                                                  'templates', 'project'))
            project_init_content = loader.load("__init__.py.txt").generate(
                project_name=project_name, module=module, component=component)
            # Generating application firenado component and handlers
            _file.write(os.path.join(project_directory, '__init__.py'),
                        project_init_content)
            handlers_file_name = os.path.join(project_directory, 'handlers.py')
            _file.touch(handlers_file_name)
            project_handlers_content = loader.load("handlers.py.txt").generate(
                handlers=['Index'])
            _file.write(handlers_file_name, project_handlers_content)
            # Generating configuration
            project_conf_directory = os.path.join(project_directory, 'conf')
            os.mkdir(project_conf_directory)
            project_conf_file = os.path.join(project_conf_directory,
                                             'firenado.yaml')
            _file.touch(project_conf_file)
            project_init_content = loader.load("firenado.yaml.txt").generate(
                app_name=project_name, module=module, component=component)
            _file.write(project_conf_file, project_init_content)
        else:
            #TODO: This thing has to go. The parameter validation should be
            #TODO: executed by the argument parser.
            loader = template.Loader(os.path.join(
                firenado.conf.ROOT, 'core', 'management', 'templates', 'help'))
            help_message = loader.load("init_command_help.txt").generate()

    def add_arguments(self, parser):
        """
        Add module argument to the command parser.

        :param parser: The current parser validating the command holding this
        task.
        """
        parser.add_argument('module', help="The project module")

    def get_error_message(self, parser, exception):
        return exception.message
        

class RunApplicationTask(ManagementTask):
    """Runs a Firenado Tornado Application based
    on the it's project configuration
    """
    def run(self, namespace):
        import signal
        self.http_server = None

        # TODO get this from firenado.conf
        self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

        # TODO: Resolve module if doesn't exists
        if firenado.conf.app['pythonpath']:
            sys.path.append(firenado.conf.app['pythonpath'])

        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTSTP, self.sig_handler)
        self.application = firenado.core.TornadoApplication()
        self.http_server = tornado.httpserver.HTTPServer(
            self.application)
        self.http_server.listen(firenado.conf.app['port'])
        tornado.ioloop.IOLoop.instance().start()

    def sig_handler(self, sig, frame):
        logger.warning('Caught signal: %s', sig)
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        import time
        logger.info('Stopping http server')
        for key, component in self.application.components.iteritems():
            component.shutdown()
        self.http_server.stop()

        logger.info('Will shutdown in %s seconds ...',
                     self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        io_loop = tornado.ioloop.IOLoop.instance()

        deadline = time.time() + self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

        def stop_loop():
            now = time.time()
            if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
                logger.info('Shutdown')
        stop_loop()
