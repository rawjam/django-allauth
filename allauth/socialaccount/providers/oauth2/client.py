from django.conf import settings

import urllib
import urlparse

from allauth.socialaccount import social_requests as requests

class OAuth2Error(Exception):
		pass


class OAuth2Client(object):

		def __init__(self, request, consumer_key, consumer_secret,
								 authorization_url,
								 access_token_url,
								 callback_url,
								 scope,
								 extra_access_token_post_params={}):
				self.request = request
				self.authorization_url = authorization_url
				self.access_token_url = access_token_url
				self.callback_url = callback_url
				self.consumer_key = consumer_key
				self.consumer_secret = consumer_secret
				self.scope = ' '.join(scope)
				self.extra_access_token_post_params = extra_access_token_post_params
				self.state = None
				self.force_https = False
				
				try:
					self.force_https = settings.FORCE_USE_HTTPS
					self.callback_url = self.callback_url.replace('http://', 'https://')
				except AttributeError:
					pass
				
		def get_redirect_url(self):
				params = {
						'client_id': self.consumer_key,
						'redirect_uri': self.callback_url,
						'scope': self.scope,
						'response_type': 'code'
				}
				params.update(self.extra_access_token_post_params)
				if self.state:
						params['state'] = self.state
				return '%s?%s' % (self.authorization_url, urllib.urlencode(params))

		def get_access_token(self, code):
				params = {'client_id': self.consumer_key,
									'redirect_uri': self.callback_url,
									'grant_type': 'authorization_code',
									'client_secret': self.consumer_secret,
									'scope': self.scope,
									'code': code}
				params = dict(params.items() + self.extra_access_token_post_params.items())
				url = self.access_token_url
				# TODO: Proper exception handling
				resp = requests.post(url, params)
				access_token = None
				if resp.status_code == 200:
						if resp.headers['content-type'].split(';')[0] == 'application/json':
								data = resp.json
						else:
								data = dict(urlparse.parse_qsl(resp.content))
						
						access_token = data.get('access_token')
						refresh_token = data.get('refresh_token', None)
				if not access_token:
						raise OAuth2Error('Error retrieving access token: %s'
															% resp.content)

				return access_token, refresh_token
