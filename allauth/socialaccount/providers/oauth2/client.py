import urllib
import urlparse
import httplib2

import simplejson as json

class OAuth2Error(Exception):
    pass


class OAuth2Client(object):

    def __init__(self, request, consumer_key, consumer_secret,
                 authorization_url,
                 access_token_url,
                 callback_url,
                 scope=None,
                 extra_authorize_url_params="",
                 extra_access_token_post_params={}):
        self.request = request
        self.authorization_url = authorization_url
        self.access_token_url = access_token_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope = scope
        self.extra_authorize_url_params = extra_authorize_url_params
        self.extra_access_token_post_params = extra_access_token_post_params

    def get_redirect_url(self):
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url
        }
        if self.scope:
            scope_string = "&scope=%s" % self.scope
        else:
            scope_string = ""
        return '%s?%s%s%s' % (self.authorization_url, urllib.urlencode(params), scope_string, self.extra_authorize_url_params)

    def get_access_token(self, code):
        client = httplib2.Http()
        data = {'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
            'code': code,
            'redirect_uri': self.callback_url}
        data = dict(data.items() + self.extra_access_token_post_params.items())
        #raw_url_params = '&redirect_uri=%s' % self.callback_url
        #url = self.access_token_url + '?%s%s%s' %(urllib.urlencode(urlencode_params), raw_url_params, self.extra_access_token_url_params)
        
        # TODO: Proper exception handling
        resp, content = client.request(self.access_token_url, 'POST', urllib.urlencode(data))
        #data = dict(urlparse.parse_qsl(content))
        #access_token = data.get('access_token')
        
        data = json.loads(content)
        access_token = data.get('access_token', None)
        
        if not access_token:
            raise OAuth2Error(data.get('error', 'Unable to retrieve OAuth2 access token'))
        return access_token, data
