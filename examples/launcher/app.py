from . import handlers
from firenado import tornadoweb
from firenado.launcher import ProcessLauncher
from tornado import gen
import os


class LauncherComponent(tornadoweb.TornadoComponent):

    def __init__(self, name, application):
        super(LauncherComponent, self).__init__(name, application)
        self.launcher_path = os.path.abspath(os.path.dirname(__file__))
        self.charge_path = os.path.join(self.launcher_path, "charge")
        self.launcher = None

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]

    @gen.coroutine
    def initialize(self):
        import sys
        self.launcher = ProcessLauncher(dir=self.charge_path,
                                        logfile=sys.stderr)
        self.launcher.load()
        yield self.launcher.launch()

    def shutdown(self):
        self.launcher.shutdown()
