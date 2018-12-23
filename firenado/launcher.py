#!/usr/bin/env python
#
# Copyright 2015-2018 Flavio Garcia
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

import firenado.conf
import logging
import os
import six
import sys
from six import iteritems
from tornado import gen

if six.PY3:
    try:
        import importlib
        reload = importlib.reload
    except AttributeError:
        # PY33
        import imp
        reload = imp.reload

logger = logging.getLogger(__name__)


class FirenadoLauncher(object):

    def __init__(self, addresses=None, dir=None, port=None, socket=None):
        self.addresses = addresses
        self.dir = dir
        self.port = port
        self.socket = socket

    def load(self):
        return None

    def launch(self):
        return None


class ProcessLauncher(FirenadoLauncher):
    import pexpect

    process = None  # type: pexpect.spawn

    def __init__(self, addresses=None, dir=None, port=None, socket=None,
                 logfile=None):
        super(ProcessLauncher, self).__init__(addresses, dir, port, socket)
        self.process = None
        self.process_callback = None
        self.logfile = logfile
        self.command = None
        self.response = None

    def load(self):
        sys.base_exec_prefix
        firenado_script = os.path.join(firenado.conf.ROOT, "bin",
                                       "firenado-cli.py")
        self.command = "%s %s app run" % (sys.executable, firenado_script)
        if self.dir is not None:
            dir_parameter = "--dir=%s" % self.dir
            self.command = "%s %s" % (self.command, dir_parameter)

        if self.socket is None:
            if self.addresses is not None:
                addresses_parameter = "--port=%s" % self.addresses
                self.command = "%s %s" % (self.command, addresses_parameter)
            if self.port is not None:
                port_parameter = "--port=%s" % self.port
                self.command = "%s %s" % (self.command, port_parameter)
        else:
            socket_parameter = "--port=%s" % self.socket
            self.command = "%s %s" % (self.command, socket_parameter)

    @gen.coroutine
    def read_process(self):
        import pexpect
        self.process_callback.stop()
        try:
            yield self.process.expect(r"[C|I|W|D|E].*", async_=True)
        except pexpect.TIMEOUT:
            pass
        self.process_callback.start()

    @gen.coroutine
    def launch(self):
        import pexpect
        import tornado.ioloop
        logger.info("Launching %s" % self.command)
        parameters = {
            'command': self.command,
            'encoding': "utf-8"
        }
        if self.logfile is not None:
            parameters['logfile'] = self.logfile
        self.process = pexpect.spawn(**parameters)
        yield self.process.expect("Firenado server started successfully.",
                                  async_=True)
        self.process_callback = tornado.ioloop.PeriodicCallback(
            self.read_process,
            400
        )
        self.process_callback.start()

    @gen.coroutine
    def shutdown(self):
        import pexpect
        yield self.process.expect(pexpect.EOF)


class TornadoLauncher(FirenadoLauncher):

    def __init__(self, addresses=None, dir=None, port=None, socket=None):
        super(TornadoLauncher, self).__init__(addresses, dir, port, socket)
        self.http_server = None
        self.application = None
        self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = firenado.conf.app[
            'wait_before_shutdown']

    def load(self):
        from .tornadoweb import TornadoApplication
        if self.dir is not None:
            # TODO: This is a problem we cannot launch an app into the app
            os.chdir(self.dir)
            reload(firenado.conf)
        # TODO: Resolve module if doesn't exists
        if firenado.conf.app['pythonpath']:
            sys.path.append(firenado.conf.app['pythonpath'])
        self.application = TornadoApplication(debug=firenado.conf.app['debug'])

    def launch(self):
        import signal
        import tornado.httpserver
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        if os.name == "posix":
            signal.signal(signal.SIGTSTP, self.sig_handler)
        self.http_server = tornado.httpserver.HTTPServer(self.application)
        if firenado.conf.app['socket'] or self.socket:
            from tornado.netutil import bind_unix_socket
            socket_path = firenado.conf.app['socket']
            if self.socket:
                socket_path = self.socket
            socket = bind_unix_socket(socket_path)
            self.http_server.add_socket(socket)
            logger.info("Firenado listening at socket ""%s" %
                        socket.getsockname())
        else:
            addresses = self.addresses
            if addresses is None:
                addresses = firenado.conf.app['addresses']
            port = self.port
            if port is None:
                port = firenado.conf.app['port']
            for address in addresses:
                self.http_server.listen(port, address)
                logger.info("Firenado listening at ""http://%s:%s" % (address,
                                                                      port))
        logger.info("Firenado server started successfully.")
        tornado.ioloop.IOLoop.instance().start()

    def sig_handler(self, sig, frame):
        import tornado.ioloop
        logger.warning('Caught signal: %s', sig)
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        import time
        import tornado.ioloop
        logger.info('Stopping http server')
        for key, component in iteritems(self.application.components):
            component.shutdown()
        self.http_server.stop()

        io_loop = tornado.ioloop.IOLoop.instance()

        if self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN == 0:
            io_loop.stop()
            logger.info('Application is down.')
        else:

            logger.info('Will shutdown in %s seconds ...',
                        self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
            deadline = time.time() + self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or
                                       io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    io_loop.stop()
                    logger.info('Application is down.')
            stop_loop()
