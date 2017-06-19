import multiapp.handlers
import firenado.tornadoweb


class MultiappComponent(firenado.tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', multiapp.handlers.IndexHandler),
        ]
