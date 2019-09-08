import firenado.tornadoweb


class App1IndexHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        self.write("App1 IndexHandler output")


class App2IndexHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        self.write("App2 IndexHandler output")
