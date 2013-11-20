from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from provider import TeamboxProvider

urlpatterns = default_urlpatterns(TeamboxProvider)

