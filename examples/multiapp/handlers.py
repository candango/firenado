import firenado.tornadoweb


class IndexHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        self.write("IndexHandler output")
