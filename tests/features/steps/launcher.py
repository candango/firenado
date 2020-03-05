# -*- coding: UTF-8 -*-
#
# Copyright 2015-2020 Flavio Garcia
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


@given("We launch {application} application using process launcher at {port} "
       "port")
@async_run_until_complete
async def step_we_launch_application_using_process_launcher(context,
                                                            application, port):
    application_dir = chdir_fixture_app(application, suppress_log=True)
    context.launcher = ProcessLauncher(
        dir=application_dir, path=PROJECT_ROOT, port=port, logfile=sys.stderr)
    context.launcher.load()
    await context.launcher.launch()
    await gen.sleep(1)
    context.tester.assertTrue(context.launcher.is_alive())


@when("The application is running correctly at {port} port")
@async_run_until_complete
async def step_we_launch_application_using_process_launcher(context, port):
    http_client = AsyncHTTPClient()
    try:
        response = await http_client.fetch("http://localhost:%s" %
                                           port)
    except Exception as e:
        print("Error: %s" % e)
        context.tester.assertTrue(False)
    else:
        context.tester.assertEquals(b"IndexHandler output", response.body)
        context.tester.assertTrue(context.launcher.is_alive())


@then("We shutdown the process launcher")
def step_we_shutdown_the_process_launcher(context):
    context.tester.assertTrue(context.launcher.is_alive())
    context.launcher.shutdown()


@then("The application stops successfully")
def step_the_application_stops_successfully(context):
    context.tester.assertFalse(context.launcher.is_alive())
