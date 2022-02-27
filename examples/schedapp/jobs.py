# -*- coding: UTF-8 -*-
#
# Copyright 2015-2022 Flavio Garcia
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

from firenado.schedule import ScheduledJob
from tornado.gen import sleep


class PrintTestJob(ScheduledJob):

    def __init__(self, scheduler, **kwargs):
        super(PrintTestJob, self).__init__(scheduler, **kwargs)
        self._custom_property = kwargs.get('custom_property', None)

    def run(self):
        print("This is the custom property value: %s" % self._custom_property)


class PrintAsyncTestJob(ScheduledJob):

    def __init__(self, scheduler, **kwargs):
        super(PrintAsyncTestJob, self).__init__(scheduler, **kwargs)
        self._custom_property = kwargs.get('custom_property', None)

    async def run(self):
        print("This is the custom property value from async job: %s" %
              self._custom_property)
        await sleep(1)


class ErroredJob(ScheduledJob):

    def __init__(self, scheduler, **kwargs):
        super(ErroredJob, self).__init__(scheduler, **kwargs)
        self._custom_property = kwargs.get('custom_property', None)

    def run(self):
        error_result = 1/0
        print("This is the custom property value: %s" % self._custom_property)


class ErroredAsyncJob(ScheduledJob):

    def __init__(self, scheduler, **kwargs):
        super(ErroredAsyncJob, self).__init__(scheduler, **kwargs)
        self._custom_property = kwargs.get('custom_property', None)

    async def run(self):
        error_result = 1/0
        print("This is the custom property value: %s" % self._custom_property)
        await sleep(1)
