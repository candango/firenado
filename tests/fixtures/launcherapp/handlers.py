from firenado import tornadoweb


class IndexHandler(tornadoweb.TornadoHandler):

    def get(self):
        self.write("Get output")

    def post(self):
        self.write("Post output")
