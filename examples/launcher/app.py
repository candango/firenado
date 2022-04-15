from . import handlers
from firenado import tornadoweb
from firenado.launcher import ProcessLauncher
import os


class LauncherComponent(tornadoweb.TornadoComponent):

    def __init__(self, name, application):
        super(LauncherComponent, self).__init__(name, application)
        self.launcher_path = os.path.abspath(os.path.dirname(__file__))
        self.charge_path = os.path.join(self.launcher_path, "charge")
        self.launcher = None
        self.launcher_callback = None

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]

    def initialize(self):
        import tornado.ioloop
        self.launcher_callback = tornado.ioloop.IOLoop.current().add_callback(
            callback=self.launch_charge
        )

    async def launch_charge(self):
        import sys
        os.chdir(self.charge_path)
        self.launcher = ProcessLauncher(dir=self.charge_path,
                                        logfile=sys.stderr)
        self.launcher.load()
        await self.launcher.launch()
        os.chdir(self.launcher_path)

    def shutdown(self):
        self.launcher.shutdown()
