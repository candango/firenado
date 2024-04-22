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
from firenado.service import FirenadoService
from firenado.launcher import ProcessLauncher, TornadoLauncher
from tornado.testing import (bind_unused_port, AsyncTestCase,
                             AsyncHTTPTestCase)
from unittest import TestCase


def get_event_loop():
    """ Return a new event asyncio evenvent loop with trigerring a
    depreciation warning from Python 10.

    :return: A event loop
    """
    loop = asyncio.get_event_loop_policy().get_event_loop()
    return loop if loop else asyncio.new_event_loop()


class ServiceTestCase(TestCase):

    def setUp(self):
        """ Call the configure data connection method
        """
        self.configure_data_connected()

    def configure_data_connected(self):
        """Should be overridden with the configutation of the data connected
        instance
        """
        raise NotImplementedError()

    @property
    def data_connected(self):
        """Should be overridden by subclasses to return a data connected
        instance
        """
        raise NotImplementedError()


class TestableService(FirenadoService):
    """ Serves a data connected method directly.
    When decorating a data connected directly the service must return the
    consumer.
    """
    pass


class TornadoAsyncTestCase(AsyncTestCase):

    @property
    def launcher(self) -> ProcessLauncher:
        return self.__launcher

    def get_launcher(self) -> ProcessLauncher:
        """Should be overridden by subclasses to return a
        `firenado.launcher.TornadoLauncher`.
        """
        raise NotImplementedError()

    def http_port(self) -> int:
        return self.__port

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


class TornadoAsyncHTTPTestCase(AsyncHTTPTestCase):

    def get_launcher(self) -> TornadoLauncher:
        """Should be overridden by subclasses to return a
        `firenado.launcher.TornadoLauncher`.
        """
        raise NotImplementedError()

    def get_log_level(self):
        return None

    def get_app(self):
        import logging
        launcher = self.get_launcher()
        launcher.load()
        if self.get_log_level() is not None:
            launcher.configure_logging(level=self.get_log_level())
        else:
            launcher.configure_logging(level=logging.WARN)
        return launcher.application
