import multiapp.handlers
import firenado.tornadoweb


class App1Component(firenado.tornadoweb.TornadoComponent):

    def get_handlers(self):
        if self.is_current_app():
            return [
                (r'/', multiapp.handlers.App1IndexHandler),
            ]
        return []


class App2Component(firenado.tornadoweb.TornadoComponent):

    def get_handlers(self):
        if self.is_current_app():
            return [
                (r'/', multiapp.handlers.App2IndexHandler),
            ]
        return []
