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
from behave.api.async_step import async_run_until_complete
from firenado.launcher import ProcessLauncher
from tornado.testing import (bind_unused_port, AsyncTestCase,
                             AsyncHTTPTestCase)
from tornado.httpclient import HTTPResponse
from tornado import gen, ioloop
from typing import Any
import warnings


def get_event_loop():
    """ Return a new event asyncio evenvent loop with trigerring a
    depreciation warning from Python 10.

    :return: A event loop
    """
    loop = asyncio.get_event_loop_policy().get_event_loop()
    return loop if loop else asyncio.new_event_loop()


class ProcessLauncherTestCase(AsyncHTTPTestCase):

    @property
    def launcher(self):
        return self.__launcher

    def get_launcher(self) -> ProcessLauncher:
        """Should be overridden by subclasses to return a
        `firenado.launcher.ProcessLauncher`.
        """
        raise NotImplementedError()

    def get_http_port(self) -> int:
        """Returns the port used by the server.

        A new port is chosen for each test.
        """
        return self.__port

    @async_run_until_complete(should_close=False, loop=get_event_loop())
    async def setUp(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sock, port = bind_unused_port()
            sock.close()
            self.__port = port
            self.__launcher = self.get_launcher()
            self.__launcher.port = self.__port
            self.__launcher.load()
            self.http_client = self.get_http_client()
            self.io_loop = ioloop.IOLoop.current()
            await self.__launcher.launch()
            await gen.sleep(1)

    def get_url(self, path: str) -> str:
        """Returns an absolute url for the given path on the test server."""
        return "%s://127.0.0.1:%s%s" % (self.get_protocol(),
                                        self.get_http_port(), path)

    async def fetch(
        self, path: str, raise_error: bool = False, **kwargs: Any
    ) -> HTTPResponse:
        """Convenience method to synchronously fetch a URL.

        The given path will be appended to the local server's host and
        port.  Any additional keyword arguments will be passed directly to
        `.AsyncHTTPClient.fetch` (and so could be used to pass
        ``method="POST"``, ``body="..."``, etc).

        If the path begins with http:// or https://, it will be treated as a
        full URL and will be fetched as-is.

        If ``raise_error`` is ``True``, a `tornado.httpclient.HTTPError` will
        be raised if the response code is not 200. This is the same behavior
        as the ``raise_error`` argument to `.AsyncHTTPClient.fetch`, but
        the default is ``False`` here (it's ``True`` in `.AsyncHTTPClient`)
        because tests often need to deal with non-200 response codes.

        .. versionchanged:: 5.0
           Added support for absolute URLs.

        .. versionchanged:: 5.1

           Added the ``raise_error`` argument.

        .. deprecated:: 5.1

           This method currently turns any exception into an
           `.HTTPResponse` with status code 599. In Tornado 6.0,
           errors other than `tornado.httpclient.HTTPError` will be
           passed through, and ``raise_error=False`` will only
           suppress errors that would be raised due to non-200
           response codes.

        """
        if path.lower().startswith(("http://", "https://")):
            url = path
        else:
            url = self.get_url(path)

        return await self.http_client.fetch(url, raise_error=raise_error,
                                            **kwargs)

    def tearDown(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.http_client.close()
            AsyncTestCase.tearDown(self)
            self.__launcher.shutdown()
