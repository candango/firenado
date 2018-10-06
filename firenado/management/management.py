#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2015-2018 Flavio Garcia
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

from __future__ import (absolute_import, division,
                        print_function, with_statement)

import firenado.conf
from firenado.util.argparse_util import FirenadoArgumentError
from firenado.util.argparse_util import FirenadoArgumentParser
import logging
import os
import sys
from six import iteritems
from tornado import template

logger = logging.getLogger(__name__)

# Commands will be registered here. This is done by ManagementCommand
command_categories = dict()


def run_from_command_line():
    """ Run Firenado's management commands from a command line
    """
    for commands_conf in firenado.conf.management['commands']:
        logger.debug("Loading %s commands from %s." % (
            commands_conf['name'],
            commands_conf['module']
        ))
        exec('import %s' % commands_conf['module'])
    command_index = 1
    for arg in sys.argv[1:]:
        command_index += 1
        if arg[0] != "-":
            break
    parser = FirenadoArgumentParser(prog=os.path.split(sys.argv[0])[1])
    parser.add_argument("command", help="Command to executed")
    try:
        namespace = parser.parse_args(sys.argv[1:command_index])
        if not command_exists(namespace.command):
            show_command_line_usage(parser)
        else:
            run_command(namespace.command, sys.argv[command_index-1:])
    except FirenadoArgumentError:
        show_command_line_usage(parser, True)


def get_command_header(parser, usage_message="", usage=False):
    """ Return the command line header

    :param parser:
    :param usage_message:
    :param usage:
    :return: The command header
    """
    loader = template.Loader(os.path.join(
        firenado.conf.ROOT, 'management', 'templates', 'help'))
    return loader.load("header.txt").generate(
        parser=parser, usage_message=usage_message, usage=usage,
        firenado_version=".".join(map(str,firenado.__version__))).decode(
        sys.stdout.encoding)


def show_command_line_usage(parser, usage=False):
    """ Show the command line help
    """
    help_header_message = get_command_header(parser, "command", usage)
    loader = template.Loader(os.path.join(
        firenado.conf.ROOT, 'management', 'templates', 'help'))
    command_template = "  {0.name:15}{0.description:40}"
    help_message = loader.load("main_command_help.txt").generate(
        command_categories=command_categories,
        command_template=command_template
    ).decode(sys.stdout.encoding)
    # TODO: This print has to go. Use proper stream instead(stdout or stderr)
    print(''.join([help_header_message, help_message]))


def command_exists(command):
    """ Check if the given command was registered. In another words if it
    exists.
    """
    for category, commands in iteritems(command_categories):
        for existing_command in commands:
            if existing_command.match(command):
                return True
    return False


def run_command(command, args):
    """ Run all tasks registered in a command.
    """
    for category, commands in iteritems(command_categories):
        for existing_command in commands:
            if existing_command.match(command):
                existing_command.run(args)


class ManagementCommand(object):
    """ Defines a management command. Commands are classified by categories and
    the Firenado category is the default one. Those commands are shipped with
    the framework.
    Developers can create new categories of commands and commands and
    distribute them with their application and/or components.
    """

    def __init__(self, name, description, cmd_help, category=None,
                 sub_commands=None, tasks=None, parent=None):
        """ To register a management command it is necessary inform the
        category you the command belongs, it's name and description and a
        meaningful help to be displayed.

        :param name: Command's name
        :param description: Command's description
        :param cmd_help: Meaningful help to be displayed
        :param category: The category the command belongs to
        :param sub_commands: Sub commands aggregated into the command
        :param tasks: Tasks to be executed when this command is called
        """
        self.category = category
        self.name = name
        self.commands = self.name.split("(")
        if len(self.commands) > 1:
            self.commands[1] = "%s%s" % (self.commands[0],
                                         self.commands[1][:-1])
        self.description = description
        self.help = cmd_help
        self.sub_commands = sub_commands
        self.tasks = []
        self.parent = None
        if tasks is not None:
            if isinstance(tasks, list):
                for task in tasks:
                    self.tasks.append(task(self))
            else:
                self.tasks.append(tasks(self))
        if category is not None:
            if category not in command_categories:
                command_categories[category] = []
            command_categories[category].append(self)

    def get_help(self):
        return self.help

    def match(self, command):
        return command in self.name

    def run(self, args):
        has_sub_commands = False
        subcommands_resolved = False
        if self.sub_commands:
            has_sub_commands = True
            # TODO handle args with size 1
            unresolved_args = args[1:]
            if len(unresolved_args):
                for subcommand in self.sub_commands:
                    if subcommand.name == unresolved_args[0]:
                        subcommand.run(unresolved_args)
                        subcommands_resolved = True
                        break
        if not has_sub_commands:
            self.run_tasks(args)
        else:
            if not subcommands_resolved:
                from tornado.template import Template
                msg_help = self.get_help()
                parser = FirenadoArgumentParser(
                        prog=os.path.split(
                            sys.argv[0])[1], usage='%(prog)s [options]',)
                if isinstance(msg_help, Template):
                    msg_help = msg_help.generate(parser=parser)
                print(get_command_header(parser, msg_help, True))

    def run_tasks(self, args):
        cmd_parser = FirenadoArgumentParser(
            prog=os.path.split(sys.argv[0])[1], usage='%(prog)s [options]',)
        cmd_parser.add_argument("command", help="Command to executed")
        try:
            for task in self.tasks:
                task.add_arguments(cmd_parser)
            namespace = cmd_parser.parse_args(args)
            for task in self.tasks:
                task.run(namespace)
        except FirenadoArgumentError as error:
            command_help = ""
            for task in self.tasks:
                error_message = task.get_error_message(cmd_parser, error)
                if error_message:
                    command_help += '\n'.join([command_help, error_message])
            print(command_help)


class ManagementTask(object):
    """
    Defines a management tasks. Tasks are the concrete actions executed by a
    command.
    """
    def __init__(self, action):
        self.action = action

    def add_arguments(self, parser):
        """
        Implement this method to add arguments to the current argparse parser
        being handled by the command.
        """
        pass

    def get_help(self):
        """
        Implement this method to add a help text to the help message to be
        displayed by the command.
        """
        return None

    def get_error_message(self, parser, error):
        return error.message

    def run(self, namespace=None):
        """
        Task implementation is done here.
        """
        pass
