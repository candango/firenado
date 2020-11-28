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

from cartola import sysexits
import yaml
import logging
import os


def get_app_defaults():
    """ Return the application configuration defaults
    :return:
    """
    app = dict()
    app['default_addresses'] = ["::", "0.0.0.0"]
    app['addresses'] = app['default_addresses']
    app['component'] = None
    # TODO: Are we using current_user_key?
    app['current_user_key'] = "__FIRENADO_CURRENT_USER_KEY__"
    app['data'] = {}
    app['data']['sources'] = []
    app['id'] = None
    app['pythonpath'] = None
    app['port'] = 8888
    app['process'] = {
        'num_processes': None,
        'max_restarts': 100
    }
    app['login'] = {}
    app['login']['urls'] = {}
    app['login']['urls']['default'] = "/login"
    app['is_on_dir'] = False
    app['session'] = {
        'id_generator': "default",
    }
    app['settings'] = {}
    app['socket'] = None
    app['static_path'] = None
    app['static_url_prefix'] = "/static"
    app['type'] = "tornado"
    app['types'] = {}
    app['types']['tornado'] = {}
    app['types']['tornado']['name'] = "tornado"
    app['types']['tornado']['launcher'] = {}
    app['types']['tornado']['launcher']['class'] = "TornadoLauncher"
    app['types']['tornado']['launcher']['module'] = "firenado.launcher"
    app['url_root_path'] = None
    # Wait before shutdown is on seconds
    app['wait_before_shutdown'] = 0
    return app


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
        'NOTSET': logging.NOTSET,
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


def get_class_from_name(name):
    """ Return a class reference from the class name provided as a parameter.
    Class name must be the full class reference, in another words, the module
    with the class absolute reference.

    Example:
    >>> get_class_from_name("my.module.Myclass")

    :param basestring name: Class absolute reference.
    :return: The class resolved from the absolute reference name provided.
    """
    return get_class_from_module(
        ".".join(name.split(".")[:-1]),
        name.split(".")[-1]
    )


def get_class_from_module(module, class_name):
    """ Returns a class from a module and a class name parameters.
    This function is used by get_class_from_config and get_class_from_name.

    Example:
    >>> get_class_from_module("my.module", "MyClass")

    :param basestring module: The module name.
    :param basestring class_name: The class name.
    :return: The class resolved by the module and class name provided.
    """
    import importlib
    module = importlib.import_module(module)
    return getattr(module, class_name)


def get_class_from_config(config, index="class"):
    """ Return a class from a config dict bit containing the indexes module and
    class.

    Examples:

    When class name index into the config is class:
    >>> config = {'module': "my.module", 'class': "MyClass"}
    >>> get_class_from_config(config)

    When class name index into config is custom:
    >>> config = {'module': "my.module", 'my_class': "MyClass"}
    >>> get_class_from_config(config, index="my_class")

    :param dict config: Config containing index and module information.
    :param basestring index: Index to be used to get the class name
    :return: The class resolved at the module referred into the config.
    """
    return get_class_from_module(config['module'], config[index])


def load_yaml_config_file(path):
    """ Returns the parsed structure from a yaml config file.

    :param path: Path where the yaml file is located.
    :return: The yaml configuration represented by the yaml file.
    """
    result = None
    with open(path, 'r') as steam:
        result = yaml.safe_load(steam)
    return result


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
        config.is_multi_app = True
        process_apps_config_session(config, config_data['apps'])
        if 'app' in config_data:

            logger = logging.getLogger(__name__)
            logger.critical("Firenado is running in multi application mode. "
                            "The app section is only allowed in simple "
                            "applicaiton mode.")
            sysexits.exit_fatal(sysexits.EX_CONFIG)
    else:
        # If not the app definition is on the firenado config file
        if 'app' in config_data:
            process_app_config_section(config, config_data['app'])


# TODO: This is being used for the multi app configuration
def process_apps_config_session(config, apps_config):
    logger = logging.getLogger(__name__)

    class AppConf:
        def __init__(self):
            self.app = {}

    for app_config in apps_config:
        config.is_multi_app = True
        if 'name' in app_config:
            name = app_config['name']
            config.apps[name] = AppConf()
            config.apps[name].app = get_app_defaults()
            if 'file' in app_config:
                file = app_config['file']
                if not os.path.isabs(file):
                    file = os.path.abspath(
                        os.path.join(config.APP_CONFIG_PATH, file)
                    )
                if not os.path.exists(file):
                    logger.critical("The file %s doesn't exists. Please check"
                                    "your apps definition and inform a valid "
                                    "file." % file)
                    sysexits.exit_fatal(sysexits.EX_CONFIG)
                file_app_config = load_yaml_config_file(file)
                if "app" in file_app_config:
                    process_app_config_section(config.apps[name],
                                               file_app_config['app'])
            else:
                process_app_config_section(config.apps[name], app_config)
        else:
            logger.critical("When defining an app in the apps section the name"
                            " parameter is mandatory.")
            sysexits.exit_fatal(sysexits.EX_CONFIG)
    if config.current_app_name is None:
        for app in config.apps:
            config.current_app_name = app
            break
    if config.current_app_name in config.apps:
        config.app = config.apps[config.current_app_name].app
    else:
        logger.critical("The application %s is not defined." %
                        config.current_app_name)
        sysexits.exit_fatal(sysexits.EX_CONFIG)


def process_app_config_section(config, app_config):
    """ Processes the app section from a configuration data dict.

    :param config: The config reference of the object that will hold the
    configuration data from the config_data.
    :param app_config: App section from a config data dict.
    """
    if 'addresses' in app_config:
        config.app['addresses'] = app_config['addresses']
    if 'component' in app_config:
        config.app['component'] = app_config['component']
    if 'data' in app_config:
        if 'sources' in app_config['data']:
            config.app['data']['sources'] = app_config['data']['sources']
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
    if 'process' in app_config:
        if 'num_processes' in app_config['process']:
            config.app['process']['num_processes'] = app_config[
                'process']['num_processes']
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
    if 'wait_before_shutdown' in app_config:
        config.app['wait_before_shutdown'] = app_config['wait_before_shutdown']


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
            process_data_sources_config(config, data_config['sources'])


def process_data_sources_config_file(config, file):
    if not os.path.isabs(file):
        file = os.path.join(config.APP_CONFIG_PATH, file)
        sources_config = load_yaml_config_file(file)
        process_data_sources_config(config, sources_config)


def process_data_sources_config(config, sources_config):
    for source_config in sources_config:
        if "name" in source_config:
            config.data['sources'][source_config['name']] = source_config
            del config.data['sources'][source_config['name']]['name']
        if "file" in source_config:
            process_data_sources_config_file(config, source_config['file'])


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
        for command in management_config['commands']:
            config.management['commands'].append(command)


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
    if 'callback_hiccup' in session_config:
        config.session['callback_hiccup'] = session_config['callback_hiccup']
    if 'callback_time' in session_config:
        config.session['callback_time'] = session_config['callback_time']
    if 'prefix' in session_config:
        config.session['prefix'] = session_config['prefix']
    if 'purge_limit' in session_config:
        config.session['purge_limit'] = session_config['purge_limit']
    if 'encoder' in session_config:
        if session_config['encoder'] in config.session['encoders']:
            config.session['encoder'] = session_config['encoder']
        else:
            logger = logging.getLogger(__name__)
            logger.critical("The session encoder \"{}\" is not defined."
                            "".format(session_config['encoder']))
            sysexits.exit_fatal(sysexits.EX_CONFIG)
