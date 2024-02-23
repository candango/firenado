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

import asyncio
from tests import chdir_fixture_app, PROJECT_ROOT
from firenado.launcher import ProcessLauncher
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import bind_unused_port, gen_test, AsyncTestCase


class ProcessLauncherTestCase(AsyncTestCase):

    def setUp(self) -> None:
        import logging
        super().setUp()
        sock, port = bind_unused_port()
        sock.close()
        self.__port = port
        self.__launcher = self.get_launcher()
        self.__launcher.configure_logging(level=logging.ERROR)
        self.__launcher.port = self.__port
        self.__launcher.load()
        asyncio.run(self.__launcher.launch())

    def tearDown(self) -> None:
        self.__launcher.shutdown()
        super().tearDown()

    def get_launcher(self):
        application_dir = chdir_fixture_app("launcherapp")
        return ProcessLauncher(
            dir=application_dir, path=PROJECT_ROOT)

    @gen_test
    async def test_get(self):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(
                    f"http://localhost:{self.__port}/")
        except Exception as e:
            raise e
        self.assertEqual(response.body, b"Get output")

    @gen_test
    async def test_post(self):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(
                f"http://localhost:{self.__port}/",
                body="",
                method="POST"
            )
        except Exception as e:
            raise e
        self.assertEqual(response.body, b"Post output")
