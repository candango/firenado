# Copyright 2015-2024 Flavio Garcia
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

from .models import UserBase
from firenado.service import FirenadoService, with_service
from firenado.sqlalchemy import with_session
from sqlalchemy import select
from sqlalchemy.orm import Session


def password_digest(pass_phrase):
    import hashlib
    m = hashlib.md5()
    m.update(pass_phrase.encode('utf-8'))
    return m.hexdigest()


class UserService(FirenadoService):

    @with_session(data_source="test")
    def create(self, user_data, **kwargs):
        session: Session = kwargs.get("session")
        user = UserBase()
        user.username = user_data['username']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.password = password_digest(user_data['password'])
        user.email = user_data['email']
        with session.begin():
            session.add(user)
        return user

    @with_session(data_source="test")
    def by_username(self, username, **kwargs) -> UserBase:
        session: Session = kwargs.get("session")
        session.begin()
        stmt = select(UserBase).where(UserBase.username == username)
        user = session.scalars(stmt).one_or_none()
        session.flush()
        return user


class LoginService(FirenadoService):

    user_service: UserService

    @with_service(UserService)
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
        print(user)
        if user:
            if user.password == password_digest(password):
                return True
        return False
