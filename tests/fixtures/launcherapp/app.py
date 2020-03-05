from . import handlers
from firenado import tornadoweb


class LauncherappComponent(tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]
