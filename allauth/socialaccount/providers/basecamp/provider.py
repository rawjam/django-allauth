from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount import requests

import oauth2 as oauth
import urllib, urllib2, json, certifi

class BasecampAccount(ProviderAccount):
	BASE_URL = 'https://basecamp.com/api/v1'
	
	def get_profile_url(self):
		return '%s/people/me.json' % self.BASE_URL

	def get_avatar_url(self):
		return self.account.extra_data.get('avatar_url')

	def request_url(self, url, args={}, callback=None):
		account = self.account
		app = SocialApp.objects.get_current(self.account.get_provider().id)
		tokens = SocialToken.objects.filter(app=app, account=account).order_by('-id')

		
		if tokens:
			token = tokens[0]
			consumer = oauth.Consumer(key=app.key, secret=app.secret)
			access_token = oauth.Token(key=token.token, secret=token.token_secret)
			client = oauth.Client(consumer, access_token)
			client.ca_certs = certifi.where()
			
			if not 'http' in url:
				url = '%s%s' % (self.BASE_URL, url)
			response, data = client.request(url)
			
			if callback: callback(url, data)
			return json.loads(data)
		return None


	def __unicode__(self):
		dflt = super(BasecampAccount, self).__unicode__()
		return self.account.extra_data.get('username', dflt)


class BasecampProvider(OAuth2Provider):
	id = 'basecamp'
	name = 'Basecamp'
	package = 'allauth.socialaccount.providers.basecamp'
	account_class = BasecampAccount

	def get_default_scope(self):
		scope = ['read_projects', 'offline_access']
		return scope


providers.registry.register(BasecampProvider)
