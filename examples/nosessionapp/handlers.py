import firenado.conf
from firenado import tornadoweb


class IndexHandler(tornadoweb.TornadoHandler):

    def get(self):
        if not firenado.conf.session['enabled']:
            self.write("Session is disabled as supposed to be.<br>")
            if self.session is None:
                self.write("Handler session is None.")
            else:
                self.write("Handler session isn't None. Something wrong "
                           "happened")
        else:
            self.write("Session is enabled. Something wrong happened.")
