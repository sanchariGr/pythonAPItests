import pytest


pytest_plugins = [
    'lib.configuration',
]

@pytest.fixture(scope='session')
def api_url(configuration):
    return configuration.URL
