from firenado import security, tornadoweb


class IndexHandler(tornadoweb.TornadoHandler):

    def get(self):
        self.write("IndexHandler output")


@security.new_autenticated()
class AuthenticatedHandler(tornadoweb.TornadoHandler):
    """ Mock the handler being decorated by the security functions.
    """

    def get(self):
        self.write("Authenticated")
