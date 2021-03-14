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

from behave import fixture, use_fixture
from firenado import launcher
from unittest.case import TestCase


@fixture
def firenado_app(context, timeout=30, **kwargs):
    context.launcher = launcher.FirenadoLauncher()
    yield context.launcher


@fixture
def tester(context, timeout=1, **kwargs):
    context.tester = TestCase()
    yield context.tester


def before_all(context):
    use_fixture(tester, context)
