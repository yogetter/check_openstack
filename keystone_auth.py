import datetime
import dateutil.parser
import dateutil.tz
import requests
import simplejson as json
import os


class OSClient(object):
    """ Base class for querying the OpenStack API endpoints.

    It uses the Keystone service catalog to discover the API endpoints.
    """
    EXPIRATION_TOKEN_DELTA = datetime.timedelta(0, 30)

    def __init__(self, username="admin", password="LS8ffSxHf7TqNxdEIbL5hVsdrchXKmZ0gIMdtyoy", tenant="admin", keystone_url="http://192.168.0.250:5000/v2.0"):
        self.username = username
        self.password = password
        self.tenant_name = tenant
        self.keystone_url = keystone_url
        self.service_catalog = []
        self.tenant_id = None
        self.timeout = 30
        self.token = None
        self.valid_until = None
        self.max_retries = 10
        self.check_config()

        # Note: prior to urllib3 v1.9, retries are made on failed connections
        # but not on timeout and backoff time is not supported.
        # (at this time we ship requests 2.2.1 and urllib3 1.6.1 or 1.7.1)
        self.session = requests.Session()
        self.session.mount(
            'http://', requests.adapters.HTTPAdapter(max_retries=10))
        self.session.mount(
            'https://', requests.adapters.HTTPAdapter(max_retries=10))

        self.get_token()

    def check_config(self):
        param = {}
        if os.path.exists('/root/openrc'):
            cfg = open('/root/openrc', 'r')
            for line in cfg:
                if len(line.split(" ")) > 1:
                   param.update({line.split(" ")[1].split("=")[0] : line.split(" ")[1].split("=")[1].split("\'")[1]})
            self.username = param['OS_USERNAME']
            self.password = param['OS_PASSWORD']
            self.tenant_name = param['OS_TENANT_NAME']
            self.keystone_url = param['OS_AUTH_URL'] + "v2.0"

    def is_valid_token(self):
        now = datetime.datetime.now(tz=dateutil.tz.tzutc())
        return self.token and self.valid_until and self.valid_until > now

    def clear_token(self):
        self.token = None
        self.valid_until = None

    def get_token(self):
        self.clear_token()
        data = json.dumps({
            "auth":
            {
                'tenantName': self.tenant_name,
                'passwordCredentials':
                {
                    'username': self.username,
                    'password': self.password
                }
            }
        })
	#deubg: print("data:", data)
        r = self.make_request('post',
                              '%s/tokens' % self.keystone_url, data=data,
                              token_required=False)
	#debug: print("status:", r.status_code)
        if not r:
            return

        if r.status_code < 200 or r.status_code > 299:
            return

        data = r.json()
        self.token = data['access']['token']['id']
        self.tenant_id = data['access']['token']['tenant']['id']
        self.valid_until = dateutil.parser.parse(
            data['access']['token']['expires']) - self.EXPIRATION_TOKEN_DELTA
        self.service_catalog = []
        for item in data['access']['serviceCatalog']:
            endpoint = item['endpoints'][0]
            self.service_catalog.append({
                'name': item['name'],
                'region': endpoint['region'],
                'service_type': item['type'],
                'url': endpoint['internalURL'],
                'admin_url': endpoint['adminURL'],
            })
	#debug print(self.token)
        return self.token

    def make_request(self, verb, url, data=None, token_required=True):
        kwargs = {
            'url': url,
            'timeout': self.timeout,
            'headers': {'Content-type': 'application/json'}
        }
	#debug print("url:",url)
        if token_required and not self.is_valid_token() and \
           not self.get_token():
            return
        elif token_required:
            kwargs['headers']['X-Auth-Token'] = self.token

        if data is not None:
            kwargs['data'] = data

        func = getattr(self.session, verb.lower())

        try:
            r = func(**kwargs)
        except Exception as e:
            return

        if r.status_code == 401:
            # Clear token in case it is revoked or invalid
            self.clear_token()

        return r

