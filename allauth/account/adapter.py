from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import send_mail

from allauth.utils import import_attribute
from rawjam.core.utils.comms import send_templated_email

import app_settings

class DefaultAccountAdapter(object):

    def stash_email_verified(self, request, email):
        request.session['account_email_verified'] = email

    def is_email_verified(self, request, email):
        """
        Checks whether or not the email address is already verified
        beyond allauth scope, for example, by having accepted an
        invitation before signing up.
        """
        ret = False
        verified_email = request.session.get('account_email_verified')
        if verified_email:
            ret = verified_email.lower() == email.lower()
        return ret

    def format_email_subject(self, subject):
        prefix = app_settings.EMAIL_SUBJECT_PREFIX
        if prefix is None:
            site = Site.objects.get_current()
            prefix = "[{name}] ".format(name=site.name)
        return prefix + unicode(subject)

    def send_mail(self, template_prefix, email, context):
        """
        Sends an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        subject = render_to_string('{0}_subject.txt'.format(template_prefix), context)
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        template_name = '%s_message.txt' % template_prefix
        context['settings'] = settings

        send_templated_email(template_name, context, subject, [email], [])

    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.  Note
        that URLs passed explicitly (e.g. by passing along a `next`
        GET parameter) take precedence over the value returned here.
        """
        return settings.LOGIN_REDIRECT_URL

    def get_email_confirmation_redirect_url(self, request):
        """
        The URL to return to after successful e-mail confirmation.
        """
        if request.user.is_authenticated():
            if app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL:
                return  \
                    app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL
            else:
                return self.get_login_redirect_url(request)
        else:
            return app_settings.EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL

def get_adapter():
    return import_attribute(app_settings.ADAPTER)()

