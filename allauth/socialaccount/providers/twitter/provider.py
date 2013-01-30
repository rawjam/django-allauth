from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider
from allauth.socialaccount.models import SocialApp, SocialToken

import oauth2 as oauth
import urllib, json

class TwitterAccount(ProviderAccount):
    def get_screen_name(self):
        return self.account.extra_data.get('screen_name')

    def get_profile_url(self):
        ret = None
        screen_name = self.get_screen_name()
        if screen_name:
            ret = 'http://twitter.com/' + screen_name
        return ret

    def get_avatar_url(self):
        ret = None
        profile_image_url = self.account.extra_data.get('profile_image_url')
        if profile_image_url:
            # Hmm, hack to get our hands on the large image.  Not
            # really documented, but seems to work.
            ret = profile_image_url.replace('_normal', '')
        return ret

    def request_url(self, url, args):
        account = self.account
        app = SocialApp.objects.get_current(self.account.get_provider().id)
        tokens = SocialToken.objects.filter(app=app, account=account).order_by('-id')
        
        if tokens:
            token = tokens[0]
            consumer = oauth.Consumer(key=app.key, secret=app.secret)
            access_token = oauth.Token(key=token.token, secret=token.token_secret)
            client = oauth.Client(consumer, access_token)
            response, data = client.request('%s?%s' % (url, urllib.urlencode(args)))
            return json.loads(data)
        return None


    def __unicode__(self):
        screen_name = self.get_screen_name()
        return screen_name or super(TwitterAccount, self).__unicode__()


class TwitterProvider(OAuthProvider):
    id = 'twitter'
    name = 'Twitter'
    package = 'allauth.socialaccount.providers.twitter'
    account_class = TwitterAccount
        
        
providers.registry.register(TwitterProvider)
