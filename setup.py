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

from setuptools import setup
from pip.req import parse_requirements
import firenado

# Solution from http://bit.ly/29Yl8VN
requirements = parse_requirements('./requirements.txt', session=False)
install_requires = [str(ir.req) for ir in requirements]

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
    install_requires=install_requires,
    url='https://github.com/candango/firenado',
    packages=[
        'firenado',
        'firenado.components',
        'firenado.components.assets',
        'firenado.components.firenado',
        'firenado.conf',
        'firenado.management',
        'firenado.util',
    ],
    package_dir={'firenado': 'firenado'},
    package_data={'firenado': [
        'requirements*.txt', 'conf/*.yml', 'management/templates/*/*.txt',
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
        'firenado = firenado.management:run_from_command_line',
    ]},
)

