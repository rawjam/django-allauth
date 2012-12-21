from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class InstagramAccount(ProviderAccount):
    def get_username(self):
        return self.account.extra_data.get('username')
    
    def get_profile_url(self):
        ret = None
        username = self.get_username()
        if username:
            ret = 'http://instagram.com/' + username
        return ret
    
    def get_avatar_url(self):
        ret = None
        profile_picture = self.account.extra_data.get('profile_picture')
        return ret
    
    def __unicode__(self):
        username = self.get_username()
        return username or super(InstagramAccount, self).__unicode__()

class InstagramProvider(OAuth2Provider):
    id = 'instagram'
    name = 'Instagram'
    package = 'allauth.socialaccount.providers.instagram'
    account_class = InstagramAccount

providers.registry.register(InstagramProvider)