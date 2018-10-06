#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2015-2016 Flavio Garcia
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
from firenado.management import ManagementTask


logger = logging.getLogger(__name__)


class TestAppCommand1Task(ManagementTask):
    """ Run the command 1.
    """
    def run(self, namespace):
        logger.debug("Running TestApp Command 1")
        print("Test App Command 1")


class TestAppCommand2Task(ManagementTask):
    """ Run the command 2.
    """
    def run(self, namespace):
        logger.debug("Running TestApp Command 2")
        print("Test App Command 2")
