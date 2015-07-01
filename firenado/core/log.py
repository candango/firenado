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

import logging


def log_level_from_string(str_level):
    """ Returns the proper log level core based on a given string
    """
    levels = {
        'CRITICAL': 50,
        'ERROR': 40,
        'WARNING': 30,
        'INFO': 20,
        'DEBUG': 10,
        'NOTSET':  0,
    }
    try:
        return levels[str_level.upper()]
    except KeyError:
        pass
    except AttributeError:
        if str_level in [0, 10, 20, 30, 40, 50]:
            return str_level
    return 0


def get_logger(name):
    global log
    """ Return the logger based on the configuration found in the config file.
    """
    # TODO: Customize format and levels according the logger name
    logger = logging.getLogger(name)
    # TODO: Don't add extra handlers if parent is in the same package
    if not logger.parent.name in name:
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(log['format'])
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
    logger.setLevel(log_level_from_string(log['level']))
    logger.propate = 0
