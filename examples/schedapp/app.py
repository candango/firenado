from . import handlers
from firenado import schedule


class SchedappComponent(schedule.ScheduledTornadoComponent):

    def get_handlers(self):
        return [
            (r'/', handlers.IndexHandler),
        ]
