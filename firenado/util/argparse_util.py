#!/usr/bin/env python
#
# Copyright 2015-2019 Flavio Garcia
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

import argparse
from gettext import gettext as _


class FirenadoArgumentError(Exception):
    """ An error thrown while parsing arguments with FirenadoArgumentParser.
    """
    pass


class FirenadoArgumentParser(argparse.ArgumentParser):
    """ Argument parser that trows an exception leaving stderr untouched.
    """

    def error(self, message):
        args = {'message': message}
        message = _("%(message)s") % args
        raise FirenadoArgumentError(message)
