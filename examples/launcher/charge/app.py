from charge import handlers
from firenado import tornadoweb


class ChargeComponent(tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]
