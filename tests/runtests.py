#!/usr/bin/env python
#
# Copyright 2015-2021 Flavio Garcia
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

import unittest
from tests import (components_test, conf_test, config_test, data_test,
                   security_test, service_test, session_test, tornadoweb_test)
from tests.util import sqlalchemy_util_test, url_util_test


def suite():
    testLoader = unittest.TestLoader()
    alltests = unittest.TestSuite()
    alltests.addTests(testLoader.loadTestsFromModule(components_test))
    alltests.addTests(testLoader.loadTestsFromModule(conf_test))
    alltests.addTests(testLoader.loadTestsFromModule(config_test))
    alltests.addTests(testLoader.loadTestsFromModule(data_test))
    alltests.addTests(testLoader.loadTestsFromModule(security_test))
    alltests.addTests(testLoader.loadTestsFromModule(service_test))
    alltests.addTests(testLoader.loadTestsFromModule(session_test))
    alltests.addTests(testLoader.loadTestsFromModule(tornadoweb_test))
    alltests.addTests(testLoader.loadTestsFromModule(sqlalchemy_util_test))
    alltests.addTests(testLoader.loadTestsFromModule(url_util_test))
    return alltests


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite())
    if not result.wasSuccessful():
        exit(2)
