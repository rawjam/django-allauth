import urllib
import httplib2
from django.utils import simplejson

from allauth.socialaccount import social_requests as requests
from allauth.socialaccount.models import SocialLogin, SocialAccount
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
														  OAuth2LoginView,
														  OAuth2CallbackView)


from allauth.utils import get_user_model
from provider import InstagramProvider

User = get_user_model()

class InstagramOAuth2Adapter(OAuth2Adapter):
	provider_id = InstagramProvider.id
	access_token_url = 'https://api.instagram.com/oauth/access_token'
	authorize_url = 'https://api.instagram.com/oauth/authorize'
	profile_url = 'https://api.instagram.com/v1/users/self'
	extra_access_token_post_params = {'grant_type':'authorization_code'}

	def complete_login(self, request, app, token):
		resp = requests.get(self.profile_url, params={ 'access_token': token.token })
		extra_data = resp.json

		extra_data = extra_data['data']
		uid = str(extra_data['id'])

		name_parts = extra_data['full_name'].split(' ', 1)
		if len(name_parts) == 2:
			first_name, last_name = name_parts
		else:
			first_name, last_name = name_parts[0], ''
		user_kwargs = {'first_name': first_name, 'last_name': last_name}
		user = User(username=extra_data['username'], **user_kwargs)
		account = SocialAccount(user=user, uid=uid, extra_data=extra_data, provider=self.provider_id)
		return SocialLogin(account)

oauth2_login = OAuth2LoginView.adapter_view(InstagramOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(InstagramOAuth2Adapter)
