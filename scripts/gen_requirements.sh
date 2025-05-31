#!/bin/bash
##
## Copyright 2015-2025 Flavio Garcia
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## gen_requirements.sh    Generate requirements txt files using pip-compile
## pip-tools
##
## Author: Flavio Garcia <piraz@candango.org>

cd requirements
pip-compile --strip-extras all.in
pip-compile --strip-extras basic.in
pip-compile --strip-extras development.in
pip-compile --strip-extras pexpect.in
pip-compile --strip-extras redis.in
pip-compile --strip-extras schedule.in
pip-compile --strip-extras sqlalchemy.in
pip-compile --strip-extras tests.in
cd --
