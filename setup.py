#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
#
# Copyright 2013-2014 Flavio Garcia
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

from setuptools import setup
import firenado

install_requires = [
    "pyyaml>=3.11",
    "tornado>=4.2.1",
]

setup(
    name='Firenado',
    version=".".join(map(str,firenado.__version__)),
    description='Componentized web framework based on Tornado.',
    license='Apache License V2.0',
    author='Flavio Garcia',
    author_email='piraz@candango.org',
    install_requires=install_requires,
    url='http://www.firenado.io/',
    packages=[
        'firenado',
        'firenado.components',
        'firenado.components.assets',
        'firenado.components.firenado',
        'firenado.conf',
        'firenado.core',
        'firenado.core.data',
        'firenado.core.management',
        'firenado.core.management.tasks',
        'firenado.util',
    ],
    package_dir={'firenado': 'firenado'},
    package_data={'firenado': [
        'conf/*.yaml', 'core/management/templates/*/*.txt',
        'components/*/conf/*.yaml.example',
        'components/*/templates/*.html',
        'components/*/static/css/*.css',
        'components/*/static/js/*.js',
        'components/*/static/js/locales/*',
        'components/*/static/js/views/*.ejs',

    ]},
    classifiers=[
        'Development Status :: 1 - Planning',
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
        'firenado = firenado.core.management:run_from_command_line',
    ]},
)

