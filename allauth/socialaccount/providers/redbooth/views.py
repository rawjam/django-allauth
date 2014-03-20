from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount import requests
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.utils import get_user_model

from provider import RedboothProvider

User = get_user_model()

class RedboothOAuth2Adapter(OAuth2Adapter):
    provider_id = RedboothProvider.id
    access_token_url = 'https://redbooth.com/oauth/token'
    authorize_url = 'https://redbooth.com/oauth/authorize'
    profile_url = 'https://redbooth.com/api/1/account'

    def complete_login(self, request, app, token):
        resp = requests.get(self.profile_url,
                            params={ 'access_token': token.token },
                            disable_ssl_certificate_validation=True)
        extra_data = resp.json
        uid = str(extra_data['id'])
        user = User(username=extra_data.get('username', ''),
                    email=extra_data.get('email', ''),
                    first_name=extra_data.get('first_name', ''),
                    last_name=extra_data.get('last_name', ''),
                    )
        account = SocialAccount(user=user,
                                uid=uid,
                                extra_data=extra_data,
                                provider=self.provider_id)
        return SocialLogin(account)


oauth2_login = OAuth2LoginView.adapter_view(RedboothOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(RedboothOAuth2Adapter)
