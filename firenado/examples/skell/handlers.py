import firenado.core


class IndexHandler(firenado.core.TornadoHandler):

    def get(self):
        self.write("IndexHandler output")


