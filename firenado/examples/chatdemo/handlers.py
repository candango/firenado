import firenado.core
import tornado.escape
from tornado import gen
import uuid


class MainHandler(firenado.core.TornadoHandler):

    def get(self):
        print self.component.message_buffer
        self.render("index.html",
                    messages=self.component.message_buffer.cache)


class MessageNewHandler(firenado.core.TornadoHandler):

    def post(self):
        message = {
            "id": str(uuid.uuid4()),
            "body": self.get_argument("body"),
        }
        # to_basestring is necessary for Python 3's json encoder,
        # which doesn't accept byte strings.
        message["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=message))
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)
        self.component.message_buffer.new_messages([message])


class MessageUpdatesHandler(firenado.core.TornadoHandler):

    @gen.coroutine
    def post(self):
        cursor = self.get_argument("cursor", None)
        # Save the future returned by wait_for_messages so we can cancel
        # it in wait_for_messages
        self.future = self.component.message_buffer.wait_for_messages(
            cursor=cursor)
        messages = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))

    def on_connection_close(self):
        self.component.message_buffer.cancel_wait(self.future)
