#!/usr/bin/env python
#
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

import firenado
from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()


# Solution from http://bit.ly/29Yl8VN
def resolve_requires(requirements_file):
    requires = []
    if os.path.isfile(f"./{requirements_file}"):
        file_dir = os.path.dirname(f"./{requirements_file}")
        with open(f"./{requirements_file}") as f:
            for raw_line in f.readlines():
                line = raw_line.strip().replace("\n", "")
                if len(line) > 0:
                    if line.startswith("-r "):
                        partial_file = os.path.join(file_dir, line.replace(
                            "-r ", ""))
                        partial_requires = resolve_requires(partial_file)
                        requires = requires + partial_requires
                        continue
                    requires.append(line)
    return requires


setup(
    name="Firenado",
    version=firenado.get_version(),
    description="Firenado is a python web framework based on Tornado web "
                "framework/server.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=firenado.__licence__,
    author=firenado.get_author(),
    author_email=firenado.get_author_email(),
    maintainer=firenado.get_author(),
    maintainer_email=firenado.get_author_email(),
    install_requires=resolve_requires("requirements/basic.txt"),
    python_requires=">= 3.8",
    extras_require={
        'all': resolve_requires("requirements/all.txt"),
        'redis': resolve_requires("requirements/redis.txt"),
        'pexpect': resolve_requires("requirements/pexpect.txt"),
        'schedule': resolve_requires("requirements/schedule.txt"),
        'sqlalchemy': resolve_requires("requirements/sqlalchemy.txt"),
    },
    url="https://github.com/candango/firenado",
    packages=find_packages(),
    package_dir={'firenado': "firenado"},
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    scripts=["firenado/bin/firenado-cli.py"],
    entry_points={'console_scripts': [
        "firenado = firenado.management:run_from_command_line",
    ]},
)
