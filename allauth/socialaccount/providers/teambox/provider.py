from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount import social_requests as requests


class TeamboxAccount(ProviderAccount):
	BASE_URL = 'https://teambox.com/api/1'
	
	def get_profile_url(self):
		return '%s/account' % self.BASE_URL

	def get_avatar_url(self):
		return self.account.extra_data.get('avatar_url')

	def request_url(self, url, args={}, callback=None):
		account = self.account
		app = SocialApp.objects.get_current(self.account.get_provider().id)
		tokens = SocialToken.objects.filter(app=app, account=account).order_by('-id')
		
		if tokens:
			token = tokens[0]
			args.update({
				'access_token': token.token,
			})
			
			url = '%s%s' % (self.BASE_URL, url)
			response = requests.get(url, args)
			
			if callback: callback(url, response.content)
			return response.json
		return None


	def __unicode__(self):
		dflt = super(TeamboxAccount, self).__unicode__()
		return self.account.extra_data.get('username', dflt)


class TeamboxProvider(OAuth2Provider):
	id = 'teambox'
	name = 'Teambox'
	package = 'allauth.socialaccount.providers.teambox'
	account_class = TeamboxAccount

	def get_default_scope(self):
		scope = ['read_projects', 'offline_access']
		return scope
	
providers.registry.register(TeamboxProvider)
