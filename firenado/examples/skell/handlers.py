import firenado.core


class IndexHandler(firenado.core.TornadoHandler):

    def get(self):
        self.write("IndexHandler output")

class SessionHandler(firenado.core.TornadoHandler):

    def get(self):
        counter = 0
        if self.session.has('counter'):
            counter = self.session.get('counter')
        counter += 1
        self.session.set('counter', counter)
        self.write("Counter: %i" % counter)
        #self.render("index.html", initial_message="Hello world!!!")
