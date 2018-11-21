from nosessionapp import handlers
from firenado import tornadoweb


class NosessionappComponent(tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]
