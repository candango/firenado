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
from firenado.testing import TornadoAsyncHTTPTestCase, TornadoAsyncTestCase
from firenado.launcher import ProcessLauncher, TornadoLauncher
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import gen_test


class AsyncTestCase(TornadoAsyncTestCase):

    def get_launcher(self):
        application_dir = chdir_fixture_app("launcherapp")
        return ProcessLauncher(
            dir=application_dir, path=PROJECT_ROOT)

    @gen_test
    async def test_get(self):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(
                    f"http://localhost:{self.http_port()}/")
        except Exception as e:
            raise e
        self.assertEqual(response.body, b"Get output")

    @gen_test
    async def test_post(self):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(
                f"http://localhost:{self.http_port()}/",
                body="",
                method="POST"
            )
        except Exception as e:
            raise e
        self.assertEqual(response.body, b"Post output")


class AsyncHTTPTestCase(TornadoAsyncHTTPTestCase):

    def get_launcher(self):
        application_dir = chdir_fixture_app("launcherapp")
        return TornadoLauncher(
            dir=application_dir, path=PROJECT_ROOT)

    def test_get(self):
        response = self.fetch("/")
        # print(response.code)
        self.assertEqual(response.body, b"Get output")

    def test_post(self):
        response = self.fetch("/", body="", method="POST")
        # print(response.code)
        self.assertEqual(response.body, b"Post output")
