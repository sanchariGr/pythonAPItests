import requests
import urllib
import logging
from http import HTTPStatus

def _log_request(logger, method, url, headers, params, data):
    logger.info(
        'Request: %s %r',
        method, url
    )

def _log_response(logger, resp):
    logger.info(
        'Response code: %r',
        resp.status_code
    )



def request_api(
        method, base_url, path, access_token=None, **kwargs
    ):
    """
    Sends request to  API and logs it
    Logging here can be configured with :class:`ApiLogConfig` class
    :param str method: http method (GET, POST, DELETE, HEAD, PUT, OPTIONS, PATCH)
    :param str base_url: base url of the API server
    :param str path: API endpoint path
    :param str access_token: access token value if any
    :param dict kwargs:
    :return: API response
    :rtype: requests.Response
    """
    full_url = urllib.parse.urljoin(base_url, path)
    full_url = full_url.format(**kwargs)
    headers = {}

    if 'headers' in kwargs:
        headers = kwargs['headers']
        del kwargs['headers']

    if access_token is not None:
        headers['Authorization'] = 'Bearer ' + access_token


    request_kwargs = {
        key: value
        for key, value in kwargs.items()
            if key in (
                'params',
                'data',
                'headers',
                'cookies',
                'files',
                'auth',
                'timeout',
                'allow_redirects',
                'proxies',
                'hooks',
                'stream',
                'verify',
                'cert',
                'json'
            )
        }
    fail_timeout = kwargs.get('fail_timeout', None)
    logger = logging.getLogger('api_request')
    _log_request(logger, method, full_url, headers, kwargs.get('params'), kwargs.get('data'))
    session = SessionManager.get_session()

    resp = session.request(
        method,
        full_url,
        headers=headers,
        **request_kwargs
    )

    _log_response(logger, resp)
    logger.debug(
        'Response time: %s',
        resp.elapsed
    )

    if fail_timeout and \
            (resp.elapsed.seconds > fail_timeout) and \
            resp.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.CREATED):
        raise TimeoutError(f'Request took longer than {fail_timeout} seconds')


    return resp

class SessionManager:
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()

        return cls._session

class ApiHelper:
    pass
