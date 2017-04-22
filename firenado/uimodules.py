
import firenado.conf
from .util.url_util import rooted_path
import tornado.web


class RootedPath(tornado.web.UIModule):

    def render(self, path):
        root = firenado.conf.app['url_root_path']
        return rooted_path(root, path)