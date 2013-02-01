from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.template import RequestContext

from allauth.utils import import_callable
from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.models import SocialApp, SocialToken

from locale import get_default_locale_callable

import urllib, urllib2, urlparse, datetime, json


class FacebookAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        uid = self.account.uid
        return 'http://graph.facebook.com/%s/picture?type=large' % uid

    def build_token_args(self, social_app, social_token):
        return {
            'access_token': social_token.token,
        }
    
    def request_url(self, url, args):
        account = self.account
        app = SocialApp.objects.get_current(self.account.get_provider().id)
        tokens = SocialToken.objects.filter(app=app, account=account).order_by('-id')
        
        if tokens:
            token = tokens[0]
            args.update(self.build_token_args(app, token))
            request_url = '%s?%s' % (url, urllib.urlencode(args))
            return json.load(urllib2.urlopen(request_url))
        
        return None

    def update_token(self, social_app, social_token):
        request_url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=fb_exchange_token&fb_exchange_token=%s' % (
            social_app.key, social_app.secret, social_token.token)
        try:
            response = urlparse.parse_qs(urllib2.urlopen(request_url).read())
            new_token = response.get('access_token', [None])[0]
            timeleft = response.get('expires', [0])[0]
            if new_token and timeleft:
                expiry_date = datetime.datetime.now() + datetime.timedelta(seconds=int(timeleft)+60)
                social_token.token = new_token
                social_token.save(expiry_date=expiry_date, updated=True)
                
        except urllib2.HTTPError, e:
            print 'Request URL:\n%s\n\nError:\n%s' % (request_url, e.read() or 'Unknown error')

    def __unicode__(self):
        dflt = super(FacebookAccount, self).__unicode__()
        return self.account.extra_data.get('name', dflt)


class FacebookProvider(OAuth2Provider):
    id = 'facebook'
    name = 'Facebook'
    package = 'allauth.socialaccount.providers.facebook'
    account_class = FacebookAccount

    def __init__(self):
        self._locale_callable_cache = None
        super(FacebookProvider, self).__init__()

    def get_method(self):
        return self.get_settings().get('METHOD', 'oauth2')

    def get_login_url(self, request, **kwargs):
        method = kwargs.get('method', self.get_method())
        if method == 'js_sdk':
            next = "'%s'" % (kwargs.get('next') or '')
            ret = "javascript:FB_login(%s)" % next
        else:
            assert method == 'oauth2'
            ret = super(FacebookProvider, self).get_login_url(request,
                                                              **kwargs)
        return ret

    def _get_locale_callable(self):
        settings = self.get_settings()
        f = settings.get('LOCALE_FUNC')
        if f:
            f = import_callable(f)
        else:
            f = get_default_locale_callable()
        return f

    def get_locale_for_request(self, request):
        if not self._locale_callable_cache:
            self._locale_callable_cache = self._get_locale_callable()
        return self._locale_callable_cache(request)

    def get_default_scope(self):
        scope = []
        if QUERY_EMAIL:
            scope.append('email')
        return scope

    def media_js(self, request):
        perms = ','.join(self.get_scope())
        locale = self.get_locale_for_request(request)
        try:
            app = self.get_app(request)
        except SocialApp.DoesNotExist:
            raise ImproperlyConfigured("No Facebook app configured: please"
                                       " add a SocialApp using the Django"
                                       " admin")
        ctx =  {'facebook_app': app,
                'facebook_channel_url':
                request.build_absolute_uri(reverse('facebook_channel')),
                'facebook_perms': perms,
                'facebook_jssdk_locale': locale}
        return render_to_string('facebook/fbconnect.html',
                                ctx,
                                RequestContext(request))

providers.registry.register(FacebookProvider)
