# Copyright 2015-2023 Flavio Garcia
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

import functools
from inspect import isfunction, ismethod
import logging
from sqlalchemy import inspect, func, text

logger = logging.getLogger(__name__)


def base_to_dict(base, columns=None):
    """ Returns a dict inherited from Base. If keys is provided it will only
    add to the dict the columns provided.
    :param base: An orm object inherited from Base
    :param columns: Columns to be added to the dict
    :return dict: A dictionary representing the Base object.
    """
    if columns is None:
        return {c.key: getattr(base, c.key)
                for c in inspect(base).mapper.column_attrs}
    return {c.key: getattr(base, c.key)
            for c in inspect(base).mapper.column_attrs if c.key in columns}


def fast_count(query):
    """
    based on https://gist.github.com/hest/8798884
    :return:
    """
    count_statement = query.statement.with_only_columns(
        [func.count()]).order_by(None)
    count = query.session.execute(count_statement).scalar()
    return count


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
    logger.debug("Opening script %s.", script_path)
    with open(script_path, "r") as stream:
        sql_command = ""
        for line in stream:
            # Ignore commented lines
            if not line.startswith("--") and line.strip("\n"):
                # Append line to the command string
                if handle_line is not None:
                    logger.debug("Calling the handle line function for: %s.",
                                 line)
                    line = handle_line(line)
                sql_command = "%s%s" % (sql_command, line.strip("\n"))
                # If the command string ends with ";", it is a full statement
                if sql_command.endswith(";"):
                    # Try to execute statement and commit it
                    try:
                        if handle_command is not None:
                            logger.debug("Calling the handle command function "
                                         "for: %s.", sql_command)
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


def with_session(*args, **kwargs):
    """ This decorator will add an existing sqlalchemy session to the method
    being decorated or create a new sqlalchemy session to be used by the
    method."""
    service = None
    if len(args) > 0:
        service = args[0]

    def method_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *method_args, **method_kwargs):
            session = method_kwargs.get("session")
            close = kwargs.get("close", False)
            close = method_kwargs.get("close", close)
            if not session:
                # If a new session is created we must close it after running
                # the method
                close = True
                data_source = kwargs.get("data_source")
                data_source = method_kwargs.get("data_source", data_source)
                if not data_source:
                    hasattr(self, "default_data_source")
                    if hasattr(self, "default_data_source"):
                        if ismethod(self.default_data_source):
                            data_source = self.default_data_source()
                        else:
                            data_source = self.default_data_source
                try:
                    if isinstance(data_source, str):
                        ds = self.get_data_source(data_source)
                        method_kwargs['data_source'] = data_source
                        session = ds.session
                    else:
                        session = data_source.session
                    method_kwargs['session'] = session
                except KeyError:
                    logger.exception("There is no datasource defined with "
                                     "index \"%s\" related to the service.",
                                     data_source)
            result = method(self, *method_args, **method_kwargs)
            if close:
                if not session:
                    logger.warning("No session was resolved.")
                logger.debug("Closing session %s.", session)
                if hasattr(session, "autoflush") and not session.autoflush:
                    session.flush()
                session.close()
            return result
        return wrapper
    # If the decorator has no parameter, I mean no parentesis, we need to wrap
    # the service variable again , instead of the service instance, we need to
    # deal with the method being decorated but as a <function> instace.
    if isfunction(service):
        @functools.wraps(None)
        def func_wrapper(_function):
            return method_wrapper(_function)
        return func_wrapper(service)
    return method_wrapper
