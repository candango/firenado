# Copyright 2015-2024 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import tornadoweb
from cartola import xray
import functools
import inspect
from json.decoder import JSONDecodeError
import logging
from tornado import escape
from tornado.web import HTTPError
import warnings

logger = logging.getLogger(__name__)


try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3


# TODO: I think we don't need a credential object. Looks like this is being
# changing to a generic metadata collection/holder to put on the session when
# the user is authenticated.
class Credential(object):

    def __init__(self):
        self.__authenticated = False

    def is_authenticated(self):
        return self.__authenticated

    def set_authenticated(self, authenticated):
        self.__authenticated = authenticated


# TODO: I think this needs to go
class Secured(object):
    @property
    def credential(self):
        """Returns the credential object """
        return self.__get_credential(self, '__credential_object', Credential)

    def __get_credential(self, obj, credential_attribute, credential_class):
        if not hasattr(obj, credential_attribute):
            setattr(obj, credential_attribute, credential_class())
        return getattr(obj, credential_attribute)


def secured(cls):
    for name, method in cls.__dict__.iteritems():
        if hasattr(method, "use_class"):
            # do something with the method and class
            print(name, cls)
    return cls


def identify(method):
    """ Decorator that gets all security data from session and adds to a
    credential.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # TODO finish the session -> credential identification
        if self.session.get('UserId') is None:
            self.credential.set_authenticated(False)
        else:
            self.credential.set_authenticated(True)
        return method(self, *args, **kwargs)
    return wrapper


def only_xhr(method):
    """ Decorates a method in a handler to only accepts XMLHttpRequest
    requests.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if "X-Requested-With" in self.request.headers:
            if self.request.headers['X-Requested-With'] == "XMLHttpRequest":
                return method(self, *args, **kwargs)
        else:
            self.set_status(403)
            self.write("This is a XMLHttpRequest request only.")
    return wrapper


def default_get_current_user(self: tornadoweb.TornadoHandler):
    user_data = self.session.get("user")
    if user_data:
        # TODO: Let's think about this better, maybe we need some parameters
        # to figure out how to customize the conversion of user_data to
        # a python object. Meanwhile this is enough for most of the cases as
        # we're mostly echanging json around anyways.
        try:
            return escape.json_decode(user_data)
        except JSONDecodeError:
            logger.info("Cannot decode user_data %s to json. Rerturning raw "
                        "data.", user_data)
            return user_data
    return None


def default_class_authentication(self: tornadoweb.TornadoHandler):
    print("AAAA")
    print(self.get_current_user)
    print("AAAA")
    import firenado.conf
    if "login" in firenado.conf.app:
        warnings.warn("The \"login\" configuration in the application %s is"
                      "depreciated. Please replace the configuration "
                      "app.login to app.security.auth instead.",
                      DeprecationWarning, 2)
    login_urls = self.get_rooted_path(
        firenado.conf.app['login']['urls']['default']
    )

    def must_login():
        decorators = xray.methods_decorators(self.__class__)
        method = self.request.method.lower()
        skip_auth_found = False
        skip_auth_variations = ["skip_auth", "security.skip_auth"]
        for decorator in filter(
                lambda d: "skip_auth" in d, decorators[method]):
            if decorator in skip_auth_variations:
                skip_auth_found = True
                break
        if skip_auth_found:
            logger.info("The handler at %s(method %s) is decoreated with "
                        "skip_auth. Bypassing authentication.",
                        self.request.path, method)
            return False
        login_url = self.get_rooted_path(
            firenado.conf.app['login']['urls']['default']
        )
        if login_url == self.request.path:
            logger.info("The path %s is a login url. Bypassing authentication"
                        ".", login_url)
            return False
        logger.info("Authentication is needed at %s.", self.request.path)
        return True

    if must_login():
        logger.info("Retrieving current user from the application.")
        user = self.current_user
        if not user:
            logger.info("The application has no current user logged.")
            login_url = self.get_rooted_path(
                firenado.conf.app['login']['urls']['default']
            )
            self.redirect(login_url)
            return
        logger.info("The application already has a current logged user: %s.",
                    user)


def new_autenticated(target=None, *args, **kwargs):
    """ This decorator will authenticate either a class or a method.
    If a class is decorated all http methods(i.e. get, post, delete, etc...)
    will be authenticated. There will be some options to skip the
    authentication process.
    If a method is decorated only that method will be authenticated.

    We could tell, using the authenticated decorator, that decorating a class
    is pessimistic, therefore every http requests will be blocked unless we
    skip the authentication process, and decorating a method is optimistic,
    because we'll block the method by individual basis.

    :param class|callable target:
    :param list args:
    :param dict kwargs:
    :return: A wrapped authenticaed class or method.
    """

    def build_class_authentication(cls: tornadoweb.TornadoHandler,
                                   *args, **kwargs):
        setattr(cls, "get_current_user", default_get_current_user)
        setattr(cls, "authenticate", default_class_authentication)
        print(cls)
        print(getattr(cls, "authenticate"))

        return cls

    if target is None:
        def f_wrapper(parametrized_target):
            if inspect.isclass(parametrized_target):
                return build_class_authentication(
                    parametrized_target, *args, **kwargs)
            else:
                @functools.wraps(parametrized_target)
                def parametrized_wrapper(self):
                    logger.info("buga")
                    print("buga")
                    print(self)
                    print("baaa")
                    if inspect.isclass(parametrized_target):
                        return build_class_authentication(
                            parametrized_target, *args, **kwargs)
                    print(parametrized_target)
                print("buuu")
                return parametrized_wrapper
        return f_wrapper


def authenticated(method):
    """ Decorator that checks if the user is authenticated.
    If not send the user to the login page."""
    def authenticate(self, *args, **kwargs):
        wrapped_method = kwargs.pop('wrapped_method')
        auth_url = kwargs.pop('url')
        is_authenticated = False
        # So if it has the current user than it is authenticated
        if self.current_user:
            is_authenticated = True
        if not is_authenticated:
            if self.request.method in ("GET", "HEAD"):
                self.redirect(auth_url)
                return
            raise HTTPError(403)
        return wrapped_method(self, *args, **kwargs)

    if hasattr(method, '__call__'):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            kwargs['wrapped_method'] = method
            try:
                url = self.get_login_url()
            except Exception:
                import firenado.conf
                # If url is not defined an exception will be raised
                url = firenado.conf.app['login']['urls']['default']
            # TODO: Why I'm not sending the full url anyways?
            if urlparse.urlsplit(url).scheme:
                # if login url is absolute, make next absolute too
                self.session.set('next_url', self.request.full_url())
            else:
                self.session.set('next_url', self.request.uri)
            kwargs['url'] = url
            return authenticate(self, *args, **kwargs)
        return wrapper
    else:
        def f_wrapper(par_method):
            import firenado.conf
            # Means someone added a parameter to the decorator
            url = firenado.conf.app['login']['urls'][method]

            @functools.wraps(par_method)
            def parametrized_wrapper(self, *args, **kwargs):
                kwargs['wrapped_method'] = par_method
                kwargs['url'] = url
                return authenticate(self, *args, **kwargs)
            return parametrized_wrapper
        return f_wrapper


def permissions(roles=None):
    if roles is None:
        roles = []

    def f_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        return wrapper
    return f_wrapper
