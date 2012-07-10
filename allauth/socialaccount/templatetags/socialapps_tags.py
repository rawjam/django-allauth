from django.template.defaulttags import token_kwargs
from django import template

from allauth.socialaccount.models import SocialApp

register = template.Library()

@register.assignment_tag
def get_provider_app(provider):
    try:
        return SocialApp.objects.get_current(provider)
    except SocialApp.DoesNotExist:
        return ''