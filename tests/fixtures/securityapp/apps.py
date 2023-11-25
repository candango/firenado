from . import handlers
from firenado import tornadoweb


class CurrentSecurityApp(tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
            (r'/authenticated', handlers.AuthenticatedHandler),
        ]


class LegacySecurityApp(tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]
