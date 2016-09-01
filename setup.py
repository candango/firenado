#!/usr/bin/env python
#
# Copyright 2015-2016 Flavio Garcia
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

from setuptools import setup, find_packages
from pip.req import parse_requirements
import firenado

# Solution from http://bit.ly/29Yl8VN
def resolve_requires(requirements_file):
    requirements = parse_requirements("./%s" % requirements_file,
            session=False)
    return [str(ir.req) for ir in requirements]

setup(
    name='Firenado',
    version='.'.join(map(str,firenado.__version__)),
    description='Firenado is a python web framework based on '
            'Tornado web framework/server.',
    license='Apache License V2.0',
    author='Flavio Garcia',
    author_email='piraz[at]candango.org',
    maintainer='Flavio Garcia',
    maintainer_email='piraz[at]candango.org',
    install_requires=resolve_requires("requirements.txt"),
    extras_require = {
        'redis': resolve_requires("requirements-redis.txt"),
        'sqlalchemy': resolve_requires("requirements-sqlalchemy.txt"),
    },
    url='https://github.com/candango/firenado',
    packages= find_packages(),
    package_dir={'firenado': 'firenado'},
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    scripts=['firenado/bin/firenado-cli.py'],
    entry_points={'console_scripts': [
        'firenado = firenado.management:run_from_command_line',
    ]},
)
