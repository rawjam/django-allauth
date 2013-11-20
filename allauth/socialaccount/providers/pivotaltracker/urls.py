from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from provider import PivotalTrackerProvider

urlpatterns = default_urlpatterns(PivotalTrackerProvider)

