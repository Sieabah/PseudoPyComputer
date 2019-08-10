import time
import ssl
import json
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar

import sys

class RequestApi:
    """
    Request API for the inventory system
    """

    @staticmethod
    def dress_data(data, config):
        """
        Take data and configuration of InvSys and put it in the api schema for v1
        :param data:
        :param config:
        :return:
        """
        return {
            'meta': {
                '_cid': data.get('client_id', None),
                'apikey': data.get('apikey', None) if data.get('apikey', None) else config['keypub'],
                'action': data.get('action', None),
                'serial': data.get('serial', None),
                'timestamp': int(time.time())
            },
            'data': data.get('data', None)
        }

    @staticmethod
    def urlbuilder(api, action):
        """
        Build the URL for v1 based on action given
        :param api: api url
        :param action: api action
        """
        return "/".join((api.rstrip('/'), 'v1', action))

    @staticmethod
    def create_request(url, data):
        """
        Create a general request for api url and data
        :param url: string url for the api
        :param data: dictionary of api request
        """

        # Get the URL
        url = RequestApi.urlbuilder(url, data['meta']['action'])

        # Actually bind the time of the request
        data['meta']['timestamp'] = time.time()

        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

        # Return the request
        return urllib.request.Request(url, bytes(json.dumps(data), 'utf8'), headers, method="POST")

    @staticmethod
    def handle_response(response):
        """
        From response return dictionary of the response if possible, otherwise a string
        :param response: urllib.response class
        """
        # Get the resp
        resp = response.read().decode('utf-8')
        try:
            # Try to decode the json
            return json.loads(resp)
        except ValueError:
            # Return the string itself
            return resp

    @staticmethod
    def handle_request(request):
        """
        Actually handle the request with the API server
        :param request: The request object
        """
        # Get the pseudo cookie handler
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

        # Try to get the request completed
        try:
            # Return the good request
            return RequestApi.handle_response(opener.open(request)), 200
        except urllib.error.HTTPError as err:
            # Return the data for errors with code
            return RequestApi.handle_response(err), err.code
        except ssl.CertificateError as err:
            print("-"*50)
            print("FATAL ERROR: Your api does not have a valid SSL certificate")
            print(err)
            print("-"*50)
            sys.exit(1)


    @staticmethod
    def request(config, data):
        """
        Generic request against the API
        :param config:
        :param data:
        :return:
        """
        uri = urllib.parse.urlparse(config['api'])
        if uri.scheme == '':
            config['api'] = 'https://' + uri.path

        # Do the request
        resp, code = RequestApi.handle_request(RequestApi.create_request(config['api'], data))

        # Figure out if we can test multiple schemas
        if code == 404:
            uri = urllib.parse.urlparse(config['api'])
            if uri.scheme == 'https' and not config.get('forceHTTPS', False):
                config['api'] = 'http://' + uri.path
            else:
                return resp, code
        elif code == 200:
            return resp, code
        else:
            return resp, code

        # Retry the request
        return RequestApi.request(config, data)

    @staticmethod
    def init(config, data=None):
        """
        Initial Inventory
        :param data: Inventory data
        """
        if not data:
            data = {}

        api = RequestApi.dress_data({'action': 'init', 'data': data}, config)

        return RequestApi.request(config, api)

    @staticmethod
    def post(config, data=None):
        """
        Post Inventory
        :param config: inventory configuration
        """
        if not data:
            data = {}

        data['action'] = 'post'

        data = RequestApi.dress_data(data, config)

        return RequestApi.request(config, data)

    @staticmethod
    def update(config):
        """
        Update Inventory
        :param config: inventory configuration
        """
        print("UPDATE", config)

    @staticmethod
    def rconf(config, data=None):
        """
        Requesting Configuration
        :param data: data object
        """
        if not data:
            data = {}

        data['action'] = 'rconf'

        data = RequestApi.dress_data(data, config)

        return RequestApi.request(config, data)

    @staticmethod
    def heartbeat(config, data=None):
        """
        Heartbeat
        :param config: configuration
        :param data:
        :return:
        """
        if not data:
            data = {}

        data['action'] = 'hbt'

        api = RequestApi.dress_data(data, config)

        return RequestApi.request(config, api)
