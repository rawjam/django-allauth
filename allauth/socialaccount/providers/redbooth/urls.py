from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from provider import RedboothProvider

urlpatterns = default_urlpatterns(RedboothProvider)
