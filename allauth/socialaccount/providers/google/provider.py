from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.app_settings import QUERY_EMAIL, PROVIDERS
from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount import social_requests as requests

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
    
    def has_valid_authentication(self, retry=True):
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
            
            if 'error' in response.json or 'errors' in response.json:
                if retry:
                    self.refresh_token()
                    return self.has_valid_authentication(False)
                else:
                    return False
            else:
                return True
        
        return False

    def request_url(self, url, args={}, callback=None):
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
            
            if callback: callback(url, response.content)
            return response.json
        return None

    def refresh_token(self):
        account = self.account
        app = SocialApp.objects.get_current(self.account.get_provider().id)
        tokens = SocialToken.objects.filter(app=app, account=account).order_by('-id')
        
        if tokens:
            token = tokens[0]
            
            response = requests.post('https://accounts.google.com/o/oauth2/token', {
                'client_id': app.key,
                'client_secret': app.secret,
                'refresh_token': token.token_secret,
                'grant_type': 'refresh_token'
            })
            
            if 'access_token' in response.json:
                token.token = response.json['access_token']
                token.save()

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
