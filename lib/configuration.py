import json
import os
import importlib.util
from importlib._bootstrap_external import SourceFileLoader
import pytest


class Configuration(dict):
    def __init__(self, dict_=None):
        super(Configuration, self).__init__()

        if dict_:
            self.update(dict_)

    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(f'Item {item!r} is not found in test configuration')
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __add__(self, other):
        result = Configuration(self)
        result.update(other)
        return result


@pytest.fixture(scope='session')
def configuration_file_path(request):
    cfp = request.config.option.configuration_file_path
    if cfp is None:
        return None

    if not os.path.isfile(cfp):
        raise FileNotFoundError(
            f'Can not find configuration file: {cfp!r}. Please specify valid path to the configuration file'
        )

    return cfp


@pytest.fixture(scope='session')
def configuration_command_line(request):
    # loading configuration variables provided in command line via '--var' option
    configuration_variables = request.config.option.configuration_variables
    exec_locals = {}

    if configuration_variables:
        for variable in configuration_variables:
            # pylint: disable=exec-used
            exec(variable, globals(), exec_locals)

    cfg_obj = Configuration(exec_locals)
    return cfg_obj


@pytest.fixture(scope='session')
def configuration_environment(request):
    # loading test configuration variables from environment variables
    config_dict = {}
    cfg_obj = Configuration(config_dict)
    return cfg_obj


@pytest.fixture(scope='session')
def configuration_module(configuration_file_path):
    cfg_obj = Configuration()

    if configuration_file_path:
        # loading module from provided path
        loader = SourceFileLoader('cfg', configuration_file_path)
        cfg_spec = importlib.util.spec_from_loader(loader.name, loader)
        cfg_mod = importlib.util.module_from_spec(cfg_spec)
        loader.exec_module(cfg_mod)

        for key, value in cfg_mod.__dict__.items():
            if not key.startswith('__'):
                setattr(cfg_obj, key, value)
    return cfg_obj


class ConsulConfig:
    def __init__(self, website_name):
        environment = os.environ.get('ENVIRONMENT')
        assert environment, "ENVIRONMENT variable must be set"
        self._root_config_folder = f'vault/{environment}/'

    def _decode_value(self, value):
        return value.decode('UTF-8').strip()

    def _read_folder_variables(self, folder):
        config_list = self._client.kv.get(folder, recurse=True)[1]
        if config_list is None:
            raise RuntimeError(f'No `{folder}` folder was found.')

        result = {}
        for item in config_list:
            key, value = item['Key'][len(folder):].upper(), item['Value']
            if key and value is not None and '/' not in key:
                value = self._decode_value(value)
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
        return result

    def get_config(self):
        config = self._read_folder_variables(self._root_config_folder)
        config.update(self._read_folder_variables(self._website_config_folder))
        return config


def load_variables(dashboard, override_dict=None):
    """Load test configuration from consul, return it as a dict.
    Read configuration from consul, update configuration with values from `override_dict`. Any existing
    configuration will be overridden.
    """
    dashboard_config = ConsulConfig(dashboard).get_config()
    if override_dict is not None:
        # only variables that are in all caps and do not start with underscore are loaded
        custom_config = {k: v for k, v in override_dict.items() if
                         k.isupper() and not (k.startswith('_') or callable(v))}
        dashboard_config.update(custom_config)
    return dashboard_config



@pytest.fixture(scope='session')
def configuration(configuration_module, configuration_environment, configuration_command_line):
    return configuration_module + configuration_environment + configuration_command_line


def pytest_addoption(parser):
    # config file path
    parser.addoption(
        '--cfg',
        '--config',
        action='store',
        type=str,
        required=False,
        dest='configuration_file_path',
        help='Path to the environment config'
    )

    # configuration variables (override variables from config file)
    parser.addoption(
        '--var',
        '--cfg_var',
        '--config_variable',
        action='append',
        type=str,
        required=False,
        dest='configuration_variables',
        help='Configuration variables. Valid python code required'
    )