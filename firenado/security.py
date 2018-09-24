#!/usr/bin/env python
#
# Copyright 2015-2018 Flavio Garcia
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

from __future__ import (absolute_import, division, print_function,
                        with_statement)

import functools
from tornado.web import HTTPError
import os

try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3

try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3


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
        """Returns a the credential object """
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


def authenticated(method):
    """ Decorator that checks if the user is authenticated.
    If not send the user to the login page."""
    def do_authentication(self, *args, **kwargs):
        wrapped_method = kwargs.pop('wrapped_method')
        auth_url = kwargs.pop('url')
        is_authenticated = False
        # So if has current user than it is authenticated
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
            return do_authentication(self, *args, **kwargs)
        return wrapper
    else:
        def f_wrapper(par_method):
            import firenado.conf
            # Means someone added a parameter to the decorator
            url = firenado.conf.app['login']['urls'][method]
            @functools.wraps(par_method)
            def par_wrapper(self, *args, **kwargs):
                kwargs['wrapped_method'] = par_method
                kwargs['url'] = url
                return do_authentication(self, *args, **kwargs)
            return par_wrapper
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


class KeyManager(object):

    SALT_SIZE = 24

    def generate(self, password):
        # First is hash second is salt
        # Salt is generated randomly
        return None

    def create_hash(self, password, salt):
        return None

    def validate_password(self, password, correct_hash):
        return False


class Sha512KeyManager(KeyManager):
    # following: https://crackstation.net/hashing-security.htm

    def generate(self, password):
        salt = os.urandom(self.SALT_SIZE).encode('hex')
        return "%s:%s" % (self.create_hash(password, salt), salt)

    def create_hash(self, password, salt):
        import hashlib
        salted_password = "%s%s" % (password, salt)
        return hashlib.sha512(salted_password).hexdigest()

    def validate_password(self, password, correct_hash):
        correct_hashX = correct_hash.split(':')
        canditate_hash = "%s:%s" % (
            self.create_hash(password, correct_hashX[1]), correct_hashX[1])
        return canditate_hash == correct_hash
