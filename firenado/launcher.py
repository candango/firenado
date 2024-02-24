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

from cartola import sysexits
import firenado.conf
from importlib import reload
import logging
import os
import sys

logger = logging.getLogger(__name__)


class FirenadoLauncher:

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
                if path.strip() != "" and path.strip() not in real_pythonpaths:
                    real_pythonpaths.append(path.strip())
            for path in sys.path:
                if path.strip() != "" and path.strip() not in real_pythonpaths:
                    real_pythonpaths.append(path.strip())
        sys.path = real_pythonpaths
        os.environ['PYTHONPATH'] = ":".join(real_pythonpaths)
        if self.dir is not None:
            os.chdir(self.dir)
        if self.app is not None or self.dir is not None:
            reload(firenado.conf)
        self.configure_logging()

    def configure_logging(self, **kargs):
        format = kargs.get("format", firenado.conf.log['format'])
        level = kargs.get("level", firenado.conf.log['level'])
        # Set logging basic configurations
        for handler in logging.root.handlers[:]:
            # clearing loggers, solution from: https://bit.ly/2yTchyx
            logging.root.removeHandler(handler)
        logging.basicConfig(level=level, format=format)

    def load(self):
        raise NotImplementedError()

    def launch(self):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()


class ProcessLauncher(FirenadoLauncher):
    try:
        import pexpect
        process: pexpect.spawn = None
    except ImportError:
        logger.debug("The pexpect module ins't isn't installed. Consider "
                     "installing it in order to launch applications using "
                     "ProcessLauncher.")

    def __init__(self, **settings):
        super().__init__(**settings)
        self.process = None
        self.process_callback = None
        self.process_callback_time = 100
        self.logfile = settings.get("logfile", None)
        self.command = None
        self.response = None

    def load(self):
        firenado_script = os.path.join(firenado.conf.ROOT, "bin",
                                       "firenado-cli.py")
        self.command = f"{sys.executable} {firenado_script} app run"
        if self.dir is not None:
            self.command = f"{self.command} --dir={self.dir}"
        if self.socket is None and self.addresses is not None:
            self.command = f"{self.command} --addresses={self.addresses}"
        if self.socket is None and self.port is not None:
            self.command = f"{self.command} --port={self.port}"
        if self.socket is not None:
            self.command = f"{self.command} --socke={self.socket}"

    async def read_process(self):
        import pexpect
        self.process_callback.stop()
        try:
            # Simple way to catch everything is wait for a new line:
            #
            await self.process.expect("\n", async_=True)
        except pexpect.TIMEOUT:
            logger.debug("Reached timeout, getting back in the loop.")
        self.process_callback.start()

    async def launch(self):
        import pexpect
        import tornado.ioloop
        logger.info("Launching %s", self.command)
        parameters = {
            'command': self.command,
            'encoding': "utf-8"
        }
        if self.dir:
            parameters['cwd'] = self.dir
        if self.logfile is not None:
            parameters['logfile'] = self.logfile
        self.process = pexpect.spawn(**parameters)
        await self.process.expect(
            [r"[Firenado server started successfully].*"], async_=True)
        self.process_callback = tornado.ioloop.PeriodicCallback(
            self.read_process,
            self.process_callback_time
        )
        self.process_callback.start()

    def send(self, line):
        logger.info("Sending line %s", line)
        self.process.sendline(line)

    def shutdown(self):
        logger.warning("Shutting down process launcher.")
        self.process.terminate(force=True)

    def is_alive(self):
        return self.process.isalive()


class TornadoLauncher(FirenadoLauncher):

    def __init__(self, **settings):
        super().__init__(**settings)
        self.http_server = None
        self.application = None
        self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = firenado.conf.app[
            'wait_before_shutdown']
        self.addresses = firenado.conf.app['default_addresses']
        if ((self.addresses is None or self.addresses == ['']) and
                firenado.conf.app['addresses']):
            self.addresses = firenado.conf.app['addresses']
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
        from tornado.ioloop import IOLoop
        import tornado.httpserver
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        if os.name == "posix":
            signal.signal(signal.SIGTSTP, self.sig_handler)
        self.http_server = tornado.httpserver.HTTPServer(self.application)
        if firenado.conf.app['xheaders'] is not None and isinstance(
                firenado.conf.app['xheaders'], bool):
            logger.debug("Setting http server xheaders as %s.",
                         firenado.conf.app['xheaders'])
            self.http_server.xheaders = firenado.conf.app['xheaders']
        if firenado.conf.app['xheaders'] is not None and isinstance(
                firenado.conf.app['xheaders'], bool):
            logger.warning("The xheaders defined in the application section"
                           "must be bool instead of %s. Ignoring the "
                           "configuration item.",
                           type(firenado.conf.app['xheaders']).__name__)
        listening_count = 0
        listening_what = "socket"
        if firenado.conf.app['socket'] or self.socket:
            from tornado.netutil import bind_unix_socket
            socket_path = firenado.conf.app['socket']
            if self.socket:
                socket_path = self.socket
            socket = bind_unix_socket(socket_path)
            self.http_server.add_socket(socket)
            logger.info("Firenado listening at socket %s",
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
                listening_what = f"{listening_what}s"
            logger.info("Firenado server started successfully. Listening at %s"
                        " %s.", listening_count, listening_what)
            if firenado.conf.app['process']['num_processes'] is not None:
                from tornado.process import fork_processes
                num_processes = firenado.conf.app['process']['num_processes']
                max_restarts = firenado.conf.app['process']['max_restarts']
                num_processes_alert = num_processes
                if num_processes == 0:
                    num_processes_alert = (
                        f"0 (assuming {tornado.process.cpu_count()} as cpu "
                        "count)")
                logger.info("Tornado set to start %s processes with %s max "
                            "restarts.", num_processes_alert, max_restarts)
                fork_processes(num_processes, max_restarts)
            IOLoop.current().start()
        else:
            logger.critical("Firenado unable to start.")
            sysexits.exit_fatal(sysexits.EX_SOFTWARE)

    def sig_handler(self, sig, _):
        """ Handle the signal sent to the process
        :param sig:  Signal set to the process
        :param _: Frame is not being used
        """
        from tornado.ioloop import IOLoop
        from tornado.process import task_id
        tid = task_id()
        pid = os.getpid()
        if tid is None:
            logger.warning("main process (pid %s) caught signal: %s", pid, sig)
        else:
            logger.warning("child %s (pid %s) caught signal: %s", tid, pid,
                           sig)
        IOLoop.current().add_callback_from_signal(self.shutdown)

    def add_sockets(self, port: int, address: str = None):
        from socket import gaierror
        from tornado.netutil import bind_sockets
        try:
            if address is None:
                address = "127.0.0.1"
            sockets = bind_sockets(port, address.strip())
            self.http_server.add_sockets(sockets)
            logger.info("Firenado listening at http://%s:%s.", address.strip(),
                        port)
            return True
        except gaierror:
            logger.error("Firenado failed to listen at http://%s:%s.",
                         address.strip(), port)
        except OSError:
            logger.error("Firenado failed to listen at http://%s:%s. Check if "
                         "another process is listening at this port or if you "
                         "provided a dns name and the correspondent ip in the "
                         "addresses configuration or if the machine owns the "
                         "ip Firenado will start to listen.", address, port)
        return False

    def shutdown(self):
        from tornado.ioloop import IOLoop
        from tornado.process import task_id
        import time

        def log_message(message: str, pid: int, tid: int = None):
            if tid is None:
                logger.info("main process (pid %s): %s", pid, message)
                return
            logger.info("child %s (pid %s): %s", tid, pid, message)

        tid = task_id()
        pid = os.getpid()
        log_message("stopping http server", pid, tid)
        for key, component in self.application.components.items():
            component.shutdown()
        self.http_server.stop()

        io_loop: IOLoop = IOLoop.current()

        if self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN == 0:
            io_loop.stop()
            log_message("application is down", pid, tid)
            return

        log_message(f"shutdown in {self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN}s"
                    " seconds", pid, tid)
        deadline = time.time() + self.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

        def stop_loop():
            now = time.time()
            if now < deadline:
                io_loop.add_timeout(now + 1, stop_loop)
                return
            io_loop.stop()
            log_message("application is down", pid, tid)
        stop_loop()
