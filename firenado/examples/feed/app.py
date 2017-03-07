import feed.handlers
import firenado.tornadoweb

class FeedComponent(firenado.tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/', feed.handlers.IndexHandler),
        ]
