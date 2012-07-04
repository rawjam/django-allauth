from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.models import OAuth2Provider


class InstagramAccount(ProviderAccount):
    def get_screen_name(self):
        return self.account.extra_data.get('screen_name')
    
    def get_profile_url(self):
        ret = None
        screen_name = self.get_screen_name()
        if screen_name:
            ret = 'http://instagram.com/' + screen_name
        return ret
    
    def get_avatar_url(self):
        ret = None
        profile_image_url = self.account.extra_data.get('profile_image_url')
        if profile_image_url:
            # Hmm, hack to get our hands on the large image.  Not
            # really documented, but seems to work.
            ret = profile_image_url.replace('_normal', '')
        return ret
    
    def __unicode__(self):
        screen_name = self.get_screen_name()
        return screen_name or super(InstagramAccount, self).__unicode__()

class InstagramProvider(OAuth2Provider):
    id = 'instagram'
    name = 'Instagram'
    package = 'allauth.socialaccount.providers.instagram'
    account_class = InstagramAccount

providers.registry.register(InstagramProvider)