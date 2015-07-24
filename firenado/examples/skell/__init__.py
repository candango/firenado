import skell.handlers
import firenado.core

class SkellComponent(firenado.core.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', skell.handlers.IndexHandler),
        ]
