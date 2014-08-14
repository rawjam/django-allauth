from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount import requests
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.utils import get_user_model

from provider import TrelloProvider

import oauth2 as oauth
import urllib, urllib2, json, certifi

User = get_user_model()

class TrelloOAuthAdapter(OAuthAdapter):
    provider_id = TrelloProvider.id
    request_token_url = 'https://trello.com/1/OAuthGetRequestToken'
    access_token_url = 'https://trello.com/1/OAuthGetAccessToken'
    authorize_url = 'https://trello.com/1/OAuthAuthorizeToken'
    profile_url = 'https://trello.com/1/members/me'

    def complete_login(self, request, app, token):
        consumer = oauth.Consumer(key=app.key, secret=app.secret)
        access_token = oauth.Token(key=token.token, secret=token.token_secret)
        client = oauth.Client(consumer, access_token, disable_ssl_certificate_validation=True)
        client.ca_certs = certifi.where()

        response, data = client.request(self.profile_url)

        extra_data = json.loads(data)

        full_name = extra_data.get('fullName', '').split(' ')
        user = User(
            username=extra_data.get('username', ''),
            email=extra_data.get('email', ''),
            first_name=full_name[0] if full_name else '',
            last_name=full_name[1] if len(full_name) > 1 else '',
        )
        account = SocialAccount(
            user=user,
            uid=extra_data.get('id'),
            extra_data=extra_data,
            provider=self.provider_id
        )
        return SocialLogin(account)

oauth_login = OAuthLoginView.adapter_view(TrelloOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TrelloOAuthAdapter)