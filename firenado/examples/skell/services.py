#!/usr/bin/env python
#
# Copyright 2015-2017 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License atex
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from firenado import service
from .models import UserBase
import datetime


def password_digest(pass_phrase):
    import hashlib
    m = hashlib.md5()
    m.update(pass_phrase.encode('utf-8'))
    return m.hexdigest()


class LoginService(service.FirenadoService):

    def __init__(self, handler, data_source=None):
        service.FirenadoService.__init__(self, handler, data_source)

    @service.served_by("skell.services.UserService")
    def is_valid(self, username, password):
        """ Checks if challenge username and password matches
        username and password defined on the service constructor..

        Args:
            username: A challenge username
            password: A challenge password

        Returns: Returns true if challenge username and password matches
        username and password defined on the service constructor.

        """
        user = self.user_service.by_username(username)
        if user:
            if user['pass'] == password:
                return True
        return False


class UserService(service.FirenadoService):

    def create(self, user_data):
        created_utc = datetime.datetime.utcnow()
        user = UserBase()
        user.username = user_data['username']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.password = password_digest(user_data['password'])
        user.email = user_data['last_name']

        db_session = self.get_data_source('test').session
        db_session.add(user)
        db_session.commit()
        db_session.close()
        return user

    def by_username(self, username):
        user = None
        if username == "test":
            user = {'usename': "test", 'pass': "testpass"}
        return user


