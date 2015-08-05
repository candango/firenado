import chatdemows.handlers
import firenado.core



class ChatdemoWsComponent(firenado.core.TornadoComponent):


    def get_handlers(self):
        return [
            (r'/', chatdemows.handlers.MainHandler),
            (r"/chatsocket", chatdemows.handlers.ChatSocketHandler),
        ]
