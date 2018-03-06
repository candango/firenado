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

import importlib
import yaml
import logging


def log_level_from_string(str_level):
    """ Returns the proper log level core based on a given string

    :param str_level: Log level string
    :return: The log level code
    """
    levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }
    try:
        return levels[str_level.upper()]
    except KeyError:
        pass
    except AttributeError:
        if str_level in [logging.DEBUG, logging.INFO, logging.WARNING,
                         logging.ERROR, logging.CRITICAL]:
            return str_level
    return logging.NOTSET


def get_config_from_package(package):
    """ Breaks a package string in module and class.

    :param package: A package string.
    :return: A config dict with class and module.
    """
    package_x = package.split('.')
    package_conf = {}
    package_conf['class'] = package_x[-1]
    package_conf['module'] = '.'.join(package_x[:-1][:])
    return package_conf


def get_class_from_config(config, index="class"):
    """ Returns a class from a config dict bit containing the module
    and class references.

    :param
        config: The config bit with module and class references.
        index:
    :return: The class located at the module referred by the config.
    """
    module = importlib.import_module(config['module'])
    return getattr(module, config[index])


def load_yaml_config_file(path):
    """ Returns the parsed structure from a yaml config file.

    :param path: Path where the yaml file is located.
    :return: The yaml configuration represented by the yaml file.
    """
    return yaml.safe_load(open(path, 'r'))


def process_config(config, config_data):
    """ Populates config with data from the configuration data dict. It handles
    components, data, log, management and session sections from the
    configuration data.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param config_data: The configuration data loaded from a configuration
    file.
    """
    if 'components' in config_data:
        process_components_config_section(config, config_data['components'])
    if 'data' in config_data:
        process_data_config_section(config, config_data['data'])
    if 'log' in config_data:
        process_log_config_section(config, config_data['log'])
    if 'management' in config_data:
        process_management_config_section(config, config_data['management'])
    if 'session' in config_data:
        process_session_config_section(config, config_data['session'])


def process_app_config(config, config_data):
    """ Populates config with data from the configuration data dict. It handles
    everything that process_config does plus application section.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param config_data: The configuration data loaded from a configuration
    file.
    """
    process_config(config, config_data)

    # If apps is on config data, this is running o multi app mode
    if 'apps' in config_data:
        config.app['multi'] = True
        process_apps_config_session(config, config_data['apps'])
    else:
        # If not the app definition is on the firenado config file
        if 'app' in config_data:
            process_app_config_section(config, config_data['app'])

# TODO: This is being used for the multi app configuration
def process_apps_config_session(config, apps_config):
    pass
    #print(apps_config)


def process_app_config_section(config, app_config):
    """ Processes the app section from a configuration data dict.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param app_config: App section from a config data dict.
    """
    if 'component' in app_config:
        config.app['component'] = app_config['component']
    if 'cookie_secret' in app_config:
        config.app['cookie_secret'] = app_config['cookie_secret']
    if 'data' in app_config:
        if 'sources' in app_config['data']:
            config.app['data']['sources'] = app_config['data']['sources']
    if 'debug' in app_config:
        config.app['debug'] = app_config['debug']
    if 'id' in app_config:
        config.app['id'] = app_config['id']
    if 'login' in app_config:
        if 'urls' in app_config['login']:
            for url in app_config['login']['urls']:
                config.app['login']['urls'][url['name']] = url['value']
    if 'pythonpath' in app_config:
        config.app['pythonpath'] = app_config['pythonpath']
    if 'port' in app_config:
        config.app['port'] = app_config['port']
    if 'url_root_path' in app_config:
        root_url = app_config['url_root_path'].strip()
        if root_url[0] == "/":
            root_url = root_url[1:]
        if root_url == "":
            root_url = None
        config.app['url_root_path'] = root_url
    if 'settings' in app_config:
        config.app['settings'] = app_config['settings']
    if 'socket' in app_config:
        config.app['socket'] = app_config['socket']
    if 'static_path' in app_config:
        config.app['static_path'] = app_config['static_path']
    if 'static_url_prefix' in app_config:
        config.app['static_url_prefix'] = app_config['static_url_prefix']
    if 'type' in app_config:
        config.app['type'] = app_config['type']
    if 'types' in app_config:
        for app_type in app_config['types']:
            app_type['launcher'] = get_config_from_package(
                app_type['launcher'])
            config.app['types'][app_type['name']] = app_type
    if 'xsrf_cookies' in app_config:
        config.app['xsrf_cookies'] = app_config['xsrf_cookies']


def process_components_config_section(config, components_config):
    """ Processes the components section from a configuration data dict.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param components_config: Data section from a config data dict.
    """
    for component_config in components_config:
        if 'id' not in component_config:
            raise Exception('The component %s was defined without an id.' %
                            component_config)
        component_id = component_config['id']
        if component_id not in config.components:
            config.components[component_id] = {}
            config.components[component_id]['enabled'] = False
            config.components[component_id]['config'] = {}
        if 'class' in component_config:
            class_config_x = component_config['class'].split('.')
            config.components[component_id]['class'] = class_config_x[-1]
            config.components[component_id]['module'] = '.'.join(
                class_config_x[:-1])
        if 'enabled' in component_config:
            config.components[component_id]['enabled'] = bool(
                component_config['enabled'])


def process_data_config_section(config, data_config):
    """ Processes the data configuration section from the configuration
    data dict.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param data_config: Data configuration section from a config data dict.
    """
    if 'connectors' in data_config:
        for connector in data_config['connectors']:
            config.data['connectors'][
                connector['name']] = get_config_from_package(
                connector['class'])
    if 'sources' in data_config:
        if data_config['sources']:
            for source in data_config['sources']:
                config.data['sources'][source['name']] = source
                del config.data['sources'][source['name']]['name']


def process_log_config_section(config, log_config):
    """ Processes the log section from a configuration  data dict.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param log_config: Log section from a config data dict.
    """
    if 'format' in log_config:
        config.log['format'] = log_config['format']
    if 'level' in log_config:
        config.log['level'] = log_level_from_string(log_config['level'])


def process_management_config_section(config, management_config):
    """ Processes the management section from a configuration data dict.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param management_config: Management section from a config data dict.
    """
    if 'commands' in management_config:
        config.management['commands'] = management_config['commands']


def process_session_config_section(config, session_config):
    """ Processes the session section from the configuration data dict.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param session_config: Session configuration section from a config data
    dict.
    """
    # Setting session type as file by default
    config.session['type'] = 'file'
    if 'enabled' in session_config:
        config.session['enabled'] = session_config['enabled']
    if 'type' in session_config:
        config.session['type'] = session_config['type']
        if config.session['type'] == 'file':
            if 'path' in session_config:
                config.session['file']['path'] = session_config['path']
        if config.session['type'] == 'redis':
            if 'data' in session_config:
                if 'source' in session_config['data']:
                    config.session['redis']['data']['source'] = session_config[
                        'data']['source']
    if 'handlers' in session_config:
        for handler in session_config['handlers']:
            handler_class_x = handler['class'].split('.')
            handler['class'] = handler_class_x[-1]
            handler['module'] = '.'.join(handler_class_x[:-1][:])
            config.session['handlers'][handler['name']] = handler
            del config.session['handlers'][handler['name']]['name']
    if 'encoders' in session_config:
        for encoder in session_config['encoders']:
            encoder_class_x = encoder['class'].split('.')
            encoder['encoder'] = encoder_class_x[-1]
            encoder['class'] = encoder_class_x[-1]
            encoder['module'] = '.'.join(encoder_class_x[:-1][:])
            config.session['encoders'][encoder['name']] = encoder
            del config.session['encoders'][encoder['name']]['name']
    if 'id_generators' in session_config:
        for generator in session_config['id_generators']:
            generator_ref_x = generator['function'].split('.')
            generator['function'] = generator_ref_x[-1]
            generator['module'] = '.'.join(generator_ref_x[:-1][:])
            config.session['id_generators'][generator['name']] = generator
            del config.session['id_generators'][generator['name']]['name']
    if 'name' in session_config:
        config.session['name'] = session_config['name']
    if 'life_time' in session_config:
        config.session['life_time'] = session_config['life_time']
    if 'scan_interval' in session_config:
        config.session['scan_interval'] = session_config['scan_interval']
