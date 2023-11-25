# -*- coding: UTF-8 -*-
#
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

import asyncio
from tests import chdir_fixture_app, PROJECT_ROOT
from firenado import security, testing
from firenado.launcher import ProcessLauncher
import sys
import unittest
from behave.api.async_step import async_run_until_complete


class MockApplication:

    def __init__(self):
        pass

    @property
    def ui_methods(self):
        return {}

    @property
    def ui_modules(self):
        return {}


class MockRequest:
    """ Mock the request being from the mock handler.
    """

    def __init__(self):
        self.headers = {}


class MockHandler:
    """ Mock the handler being decorated by the security functions.
    """
    def __init__(self):
        self.status = 200
        self.response = None
        self.request = MockRequest()

    def set_status(self, status):
        self.status = status

    def write(self, value):
        self.response = value

    @security.only_xhr
    def get_only_xhr(self):
        pass


class MockComponent:

    def before_request(self):
        pass


class SecurityTestCase(unittest.TestCase):

    def setUp(self):
        """ Setting up a mock handler to test security decorators.
        """
        self.handler = MockHandler()

    def test_only_xhr(self):
        """ Check if the xhr will allow the request to go when XMLHttpRequest
        is found in the headers and if a 403 will be thrown when not found.
        """
        self.handler.request.headers['X-Requested-With'] = "XMLHttpRequest"
        self.handler.get_only_xhr()
        self.assertEqual(self.handler.status, 200)
        self.assertEqual(self.handler.response, None)

        self.handler.request.headers.pop("X-Requested-With")
        self.handler.get_only_xhr()
        self.assertEqual(self.handler.status, 403)
        self.assertEqual(self.handler.response, "This is a XMLHttpRequest "
                                                "request only.")


class CurrentSecurityTestCase(testing.ProcessLauncherTestCase):

    def get_launcher(self) -> ProcessLauncher:
        application_dir = chdir_fixture_app("securityapp")
        return ProcessLauncher(
            dir=application_dir, path=PROJECT_ROOT, logfile=sys.stderr)

    # @async_run_until_complete(loop=testing.get_event_loop())
    # async def test_auth_decorated_class(self):
    #     response = await self.fetch('/authenticated')
    #     await asyncio.sleep(1)
    #     print(response.code)
    #     self.assertEqual(response.body, b'Authenticated')
