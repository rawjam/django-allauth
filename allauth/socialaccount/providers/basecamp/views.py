from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
														  OAuth2LoginView,
														  OAuth2CallbackView)
from allauth.socialaccount import requests
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.utils import get_user_model

from provider import BasecampProvider

import oauth2 as oauth
import urllib, urllib2, json, certifi

User = get_user_model()

class BasecampOAuth2Adapter(OAuth2Adapter):
	provider_id = BasecampProvider.id
	access_token_url = 'https://launchpad.37signals.com/authorization/token'
	authorize_url = 'https://launchpad.37signals.com/authorization/new'
	profile_url = 'https://launchpad.37signals.com/authorization.json'

	def complete_login(self, request, app, token):
		consumer = oauth.Consumer(key=app.key, secret=app.secret)
		access_token = oauth.Token(key=token.token, secret=token.token_secret)
		client = oauth.Client(consumer, access_token)
		client.ca_certs = certifi.where()

		response, data = client.request(self.profile_url)
		
		extra_data = json.loads(data)
		identity = extra_data['identity']
		uid = str(identity['id'])
		
		user = User(username=extra_data.get('username', ''),
					email=extra_data.get('email_address', ''),
					first_name=identity.get('first_name', ''),
					last_name=identity.get('last_name', ''),
					)
		account = SocialAccount(user=user,
								uid=uid,
								extra_data=extra_data,
								provider=self.provider_id)
		return SocialLogin(account)


class BasecampLoginView(OAuth2LoginView):
	parameters = {'type': 'web_server'}

class BasecampCallbackView(OAuth2CallbackView):
	parameters = {'type': 'web_server'}

oauth2_login = BasecampLoginView.adapter_view(BasecampOAuth2Adapter)
oauth2_callback = BasecampCallbackView.adapter_view(BasecampOAuth2Adapter)
