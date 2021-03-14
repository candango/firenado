#!/usr/bin/env python
#
# Copyright 2015-2021 Flavio Garcia
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
import sys

try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    print("error: Upgrade to a pip version newer than 10. Run \"pip install "
          "--upgrade pip\".")
    sys.exit(1)


# Solution from http://bit.ly/29Yl8VN
def resolve_requires(requirements_file):
    try:
        requirements = parse_requirements("./%s" % requirements_file,
                                          session=False)
        return [str(ir.req) for ir in requirements]
    except AttributeError:
        # for pip >= 20.1.x
        # Need to run again as the first run was ruined by the exception
        requirements = parse_requirements("./%s" % requirements_file,
                                          session=False)
        # pr stands for parsed_requirement
        return [str(pr.requirement) for pr in requirements]


def use_right_tornado(requirements):
    tornado_req = "requirements/tornado_new.txt"
    if sys.version[0] == "2":
        tornado_req = "requirements/tornado_legacy.txt"
    requirements.append(resolve_requires(tornado_req)[0])
    return requirements


with open("README.md", "r") as fh:
    long_description = fh.read()

# We still running: python setup.py sdist upload --repository=testpypi
# Twine isn't handling long_descriptions as per:
# https://github.com/pypa/twine/issues/262
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
    install_requires=use_right_tornado(resolve_requires(
        "requirements/basic.txt"
    )),
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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
