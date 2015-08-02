import skell.handlers
import firenado.core
import tornado.web
import os

class SkellComponent(firenado.core.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', skell.handlers.IndexHandler),
            (r'/session', skell.handlers.SessionHandler),
            (r"/bower_components/(.*)", tornado.web.StaticFileHandler,
             {"path": os.path.join(self.get_component_path(),
                                   'bower_components')}),
        ]
