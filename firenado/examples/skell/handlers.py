import firenado.core


class IndexHandler(firenado.core.TornadoHandler):

    def get(self):
        self.render("index.html", message="Hello world!!!")

class SessionHandler(firenado.core.TornadoHandler):

    def get(self):
        reset = details=self.get_argument("reset", False, True)
        if reset:
            self.session.delete('counter')
            self.redirect('/session')
            return None
        counter = 0
        if self.session.has('counter'):
            counter = self.session.get('counter')
        counter += 1
        self.session.set('counter', counter)
        self.render("session.html", session_value=counter)
