#!/usr/bin/env python
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

import logging
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Name as sqlalchemy_util to avoid concurrency with the original
# sqlalchemy module

Base = declarative_base()
Session = sessionmaker()
logger = logging.getLogger(__name__)


def run_script(script_path, session, handle_command=None, handle_line=None):
    """ Run a script file using a valid sqlalchemy session.

    Based on https://bit.ly/2CToAhY.
    See also sqlalchemy transaction control: https://bit.ly/2yKso0A

    :param script_path: The path where the script is located
    :param session: A sqlalchemy session to execute the sql commands from the
    script
    :param handle_command: Function to handle a valid command
    :param handle_line: Function to handle a valid line
    :return:
    """
    logger.debug("Opening script %s." % script_path)
    with open(script_path, "r") as stream:
        sql_command = ""
        for line in stream:
            # Ignore commented lines
            if not line.startswith("--") and line.strip("\n"):
                # Append line to the command string
                if handle_line is not None:
                    logger.debug("Calling the handle line function for: "
                                 "%s." % line)
                    line = handle_line(line)
                sql_command = "%s%s" % (sql_command, line.strip("\n"))
                # If the command string ends with ";", it is a full statement
                if sql_command.endswith(";"):
                    # Try to execute statement and commit it
                    try:
                        if handle_command is not None:
                            logger.debug("Calling the handle command function "
                                         "for: %s." % sql_command)
                            sql_command = handle_command(sql_command)
                        session.execute(text(sql_command))
                    # Assert in case of error
                    except Exception as e:
                        session.rollback()
                        raise e
                    # Finally, clear command string
                    finally:
                        sql_command = ""
    session.commit()
