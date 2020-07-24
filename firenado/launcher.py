# -*- coding: UTF-8 -*-
#
# Copyright 2015-2020 Flavio Garcia
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

from cartola import sysexits
import firenado.conf
import logging
import os
import six
from six import iteritems
import sys
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

    def __init__(self, **settings):
        self.app = settings.get("app", None)
        self.path = settings.get("path", None)
        if self.path is not None:
            sys.path.append(self.path)
        if self.app:
            os.environ["CURRENT_APP"] = self.app
        if os.environ.get("CURRENT_APP"):
            self.app = os.environ.get("CURRENT_APP")
        self.addresses = settings.get("addresses", None)
        self.dir = settings.get("dir", None)
        self.port = settings.get("port", None)
        self.socket = settings.get("socket", None)

        # Fixing and cleaning PYTHONPATH and sys.path
        # This is useful so we can run a process launcher with the same
        # PYTHONPATH from the parent process
        real_pythonpaths = sys.path[:]
        if "PYTHONPATH" in os.environ and os.environ['PYTHONPATH'] is not None:
            current_pythonpaths = os.environ['PYTHONPATH'].split(":")
            for path in current_pythonpaths:
                if path.strip() != "":
                    if path.strip() not in real_pythonpaths:
                        real_pythonpaths.append(path.strip())
            for path in sys.path:
                if path.strip() != "":
                    if path.strip() not in real_pythonpaths:
                        real_pythonpaths.append(path.strip())
        sys.path = real_pythonpaths
        os.environ['PYTHONPATH'] = ":".join(real_pythonpaths)

    def load(self):
        return None

    def launch(self):
        return None


class ProcessLauncher(FirenadoLauncher):
    try:
        import pexpect
        process = None  # type: pexpect.spawn
    except ImportError:
        logger.debug("The pexpect module ins't isn't installed. Consider "
                     "installing it in order to launch applications using "
                     "ProcessLauncher.")

    def __init__(self, **settings):
        super(ProcessLauncher, self).__init__(**settings)
        self.process = None
        self.process_callback = None
        self.logfile = settings.get("logfile", None)
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
            # Simple way to catch everything is wait for a new line:
            #
            yield self.process.expect("\n", async_=True)
        except pexpect.TIMEOUT:
            logger.warning("Reached timeout")
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
        yield self.process.expect(
            [r"[Firenado server started successfully].*"], async_=True)
        self.process_callback = tornado.ioloop.PeriodicCallback(
            self.read_process,
            400
        )
        self.process_callback.start()

    def send(self, line):
        logger.info("Sending line {}".format(line))
        self.process.sendline(line)

    def shutdown(self):
        logger.warning("Shutting down process launcher.")
        self.process.terminate(force=True)

    def is_alive(self):
        return self.process.isalive()


class TornadoLauncher(FirenadoLauncher):

    def __init__(self, **settings):
        super(TornadoLauncher, self).__init__(**settings)
        self.http_server = None
        self.application = None
        if self.dir is not None:
            os.chdir(self.dir)
        if self.app is not None or self.dir is not None:
            reload(firenado.conf)
        self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = firenado.conf.app[
            'wait_before_shutdown']
        if self.addresses is None or self.addresses == ['']:
            if firenado.conf.app['addresses']:
                self.addresses = firenado.conf.app['addresses']
            else:
                self.addresses = firenado.conf.app['default_addresses']
        if self.port is None:
            self.port = firenado.conf.app['port']

    def load(self):
        from .tornadoweb import TornadoApplication
        # TODO: Resolve module if doesn't exists
        if firenado.conf.app['pythonpath']:
            sys.path.append(firenado.conf.app['pythonpath'])
        self.application = TornadoApplication(**firenado.conf.app['settings'])

    def launch(self):
        import signal
        import tornado.httpserver
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        if os.name == "posix":
            signal.signal(signal.SIGTSTP, self.sig_handler)
        self.http_server = tornado.httpserver.HTTPServer(self.application)
        listening_count = 0
        listening_what = "socket"
        if firenado.conf.app['socket'] or self.socket:
            from tornado.netutil import bind_unix_socket
            socket_path = firenado.conf.app['socket']
            if self.socket:
                socket_path = self.socket
            socket = bind_unix_socket(socket_path)
            self.http_server.add_socket(socket)
            logger.info("Firenado listening at socket ""%s" %
                        socket.getsockname())
            listening_count += 1
        else:
            listening_what = "addresses:port"
            if len(self.addresses):
                for address in self.addresses:
                    if self.add_sockets(self.port, address):
                        listening_count += 1
            else:
                if self.add_sockets(self.port):
                    listening_count += 1
        if listening_count:
            if listening_count > 1:
                listening_what = "%ss" % listening_what
            logger.info("Firenado server started successfully. Listening at %s"
                        " %s." % (listening_count, listening_what))
            if firenado.conf.app['process']['num_processes'] is not None:
                import tornado.process
                num_processes = firenado.conf.app['process']['num_processes']
                max_restarts = firenado.conf.app['process']['max_restarts']
                num_processes_alert = num_processes
                if num_processes == 0:
                    num_processes_alert = ("0 (assuming %s as cpu count)" %
                                           tornado.process.cpu_count())
                logger.info("Tornado set to start %s processes with %s max "
                            "restarts." % (num_processes_alert, max_restarts))
                tornado.process.fork_processes(num_processes, max_restarts)
            tornado.ioloop.IOLoop.current().start()
        else:
            logger.critical("Firenado unable to start.")
            sysexits.exit_fatal(sysexits.EX_SOFTWARE)

    def sig_handler(self, sig, _):
        """ Handle the signal sent to the process
        :param sig:  Signal set to the process
        :param _: Frame is not being used
        """
        import tornado.ioloop
        from tornado.process import task_id
        tid = task_id()
        pid = os.getpid()
        if tid is None:
            logger.warning("main process (pid %s) caught signal: %s" %
                           (pid, sig))
        else:
            logger.warning("child %s (pid %s) caught signal: %s" %
                           (tid, pid, sig))
        tornado.ioloop.IOLoop.current().add_callback_from_signal(self.shutdown)

    def add_sockets(self, port, address=None):
        from socket import gaierror
        try:
            from tornado.netutil import bind_sockets
            if address:
                sockets = bind_sockets(port, address.strip())
            else:
                sockets = bind_sockets(port)
                address = "127.0.0.1"
            self.http_server.add_sockets(sockets)
            logger.info("Firenado listening at http://%s:%s." %
                        (address.strip(), port))
            return True
        except gaierror as error:
            logger.error("Firenado failed to listen at http://%s:%s."
                         % (address.strip(), port))
        except OSError as error:
            logger.error("Firenado failed to listen at http://%s:%s. "
                         "Check if another process is listening at "
                         "this port or if you provided a dns name and"
                         "the correspondent ip in the addresses"
                         "configuration or if the machine owns the ip "
                         "Fireando will start to listen." %
                         (address, port))
        return False

    def shutdown(self):
        import time
        import tornado.ioloop
        from tornado.process import task_id
        tid = task_id()
        pid = os.getpid()
        if tid is None:
            logger.info("main process (pid %s): stopping http server" % pid)
        else:
            logger.info("child %s (pid %s): stopping http server" % (tid, pid))
        for key, component in iteritems(self.application.components):
            component.shutdown()
        self.http_server.stop()

        io_loop = tornado.ioloop.IOLoop.current()

        if self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN == 0:
            io_loop.stop()
            if tid is None:
                logger.info("main process (pid %s): application is down" % pid)
            else:
                logger.info("child %s (pid %s): application is down" %
                            (tid, pid))
        else:
            if tid is None:
                logger.info("main process (pid %s): shutdown in %s seconds "
                            "..." %
                            (pid, self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN))
            else:
                logger.info("child %s (pid %s): shutdown in %s seconds ..." %
                            (tid, pid, self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN))
            deadline = time.time() + self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

            def stop_loop():
                now = time.time()
                if now < deadline:
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    io_loop.stop()
                    if tid is None:
                        logger.info("main process (pid %s): application is "
                                    "down" % pid)
                    else:
                        logger.info("child %s (pid %s): application is down" %
                                    (tid, pid))
            stop_loop()
