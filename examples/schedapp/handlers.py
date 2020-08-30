from firenado import tornadoweb


class IndexHandler(tornadoweb.TornadoHandler):

    def get(self):
        self.render("index.html", schedulers=self.component.schedulers)
