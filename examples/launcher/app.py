from launcher import handlers
from firenado import tornadoweb
from firenado.tornadoweb import FirenadoLauncher
import os


class LauncherComponent(tornadoweb.TornadoComponent):

    def __init__(self, name, application):
        super(LauncherComponent, self).__init__(name, application)
        self.launcher_path = os.path.abspath(os.path.dirname(__file__))
        self.charge_path = os.path.join(self.launcher_path, "charge")

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]

    def initialize(self):
        firenado_launcher = FirenadoLauncher(dir=self.charge_path)
        #firenado_launcher.load()
        #firenado_launcher.launch()

    def shutdown(self):
        print("Buga")