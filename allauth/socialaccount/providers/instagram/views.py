import urllib
import httplib2
from django.utils import simplejson

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CompleteView)


from models import InstagramProvider

class InstagramOAuth2Adapter(OAuth2Adapter):
    provider_id = InstagramProvider.id
    access_token_url = 'https://api.instagram.com/oauth/access_token'
    authorize_url = 'https://api.instagram.com/oauth/authorize'
    user_show_url = 'https://instagram.com/api/v2/json/user/show'
    scope = "comments+relationships+likes"
    extra_authorize_url_params = "&response_type=code"
    extra_access_token_post_params = {'grant_type':'authorization_code'}
    
    def get_user_info(self, request, access_token_response, app, access_token):
        """
        Example access_token_response:
        {
            'access_token': '11049101.5dbaacb.a68b1aa96921d6bd81299fac31b57849',
            'user': {
                'username': 'bendell', 'bio': 'My bio', 'website': 'http://instacanv.as/bendell',
                'profile_picture': 'http://images.instagram.com/profiles/profile_11039101_75sq_1340657329.jpg',
                'full_name': 'Benjamin Dell', 'id': '11039101'
            }
        }"""
        
        data = {
            'username': access_token_response['user']['username'],
            'full_name': access_token_response['user']['full_name'],
            'profile_picture': access_token_response['user']['profile_picture'],
            'access_token': access_token_response['access_token']
        }
        uid = str(access_token_response['user']['id'])
        extra_data = access_token_response['user']
        extra_data['access_token'] = access_token_response['access_token']
        return uid, data, extra_data

oauth2_login = OAuth2LoginView.adapter_view(InstagramOAuth2Adapter)
oauth2_complete = OAuth2CompleteView.adapter_view(InstagramOAuth2Adapter)