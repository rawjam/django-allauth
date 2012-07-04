from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from models import InstagramProvider

urlpatterns = default_urlpatterns(InstagramProvider)