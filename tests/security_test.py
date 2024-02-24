# Copyright 2015-2024 Flavio Garcia
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

from tests import chdir_fixture_app, PROJECT_ROOT
from firenado import security, testing
from firenado.launcher import TornadoLauncher
import unittest


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


class CurrentSecurityTestCase(testing.TornadoAsyncHTTPTestCase):

    def get_launcher(self):
        application_dir = chdir_fixture_app("securityapp")
        return TornadoLauncher(
            dir=application_dir, path=PROJECT_ROOT)

    def test_root(self):
        response = self.fetch("/")
        # print(response.code)
        self.assertEqual(response.body, b"IndexHandler output")

    # TODO: finish authentication tests
    # def test_auth_decorated_class(self):
    #     response = self.fetch("/authenticated")
    #     # print(response.code)
    #     self.assertEqual(response.body, b"Authenticated")
