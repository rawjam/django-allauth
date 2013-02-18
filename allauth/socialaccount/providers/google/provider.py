from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.app_settings import QUERY_EMAIL, PROVIDERS
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount import requests

import oauth2 as oauth
import urllib, json

GOOGLE_SETTINGS = PROVIDERS.get('google', {})

class Scope:
    USERINFO_PROFILE = 'https://www.googleapis.com/auth/userinfo.profile'
    USERINFO_EMAIL = 'https://www.googleapis.com/auth/userinfo.email'
    EXTRA = GOOGLE_SETTINGS.get('scope', [])


class GoogleAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')
    
    def has_valid_authentication(self):
        account = self.account
        app = SocialApp.objects.get_current(self.account.get_provider().id)
        tokens = SocialToken.objects.filter(app=app, account=account).order_by('-id')
        
        if tokens:
            token = tokens[0]
            response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', {
                'client_id': app.key,
                'client_secret': app.secret,
                'access_token': token.token,            
            })
            return not ('error' in response.json or 'errors' in response.json)
        return False

    def request_url(self, url, args):
        account = self.account
        app = SocialApp.objects.get_current(self.account.get_provider().id)
        tokens = SocialToken.objects.filter(app=app, account=account).order_by('-id')
        
        if tokens:
            token = tokens[0]
            args.update({
                'client_id': app.key,
                'client_secret': app.secret,
                'access_token': token.token,
            })
            response = requests.get(url, args)
            return response.json
        return None

    def __unicode__(self):
        dflt = super(GoogleAccount, self).__unicode__()
        return self.account.extra_data.get('name', dflt)


class GoogleProvider(OAuth2Provider):
    id = 'google'
    name = 'Google'
    package = 'allauth.socialaccount.providers.google'
    account_class = GoogleAccount

    def get_default_scope(self):
        scope = [Scope.USERINFO_PROFILE]
        if QUERY_EMAIL:
            scope.append(Scope.USERINFO_EMAIL)
        scope.extend(Scope.EXTRA)
        return scope

providers.registry.register(GoogleProvider)
