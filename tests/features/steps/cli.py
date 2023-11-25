# -*- coding: UTF-8 -*-
#
# Copyright 2015-2022 Flávio Gonçalves Garcia
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


from behave import given, when, then
from behave.api.async_step import async_run_until_complete
from tests import PROJECT_ROOT, chdir_fixture_app
from firenado.launcher import ProcessLauncher
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import sys


@given("command {command} is called")
async def command_is_called(context, command):
    context.tester.assertTrue(False)
    print("Buga")
