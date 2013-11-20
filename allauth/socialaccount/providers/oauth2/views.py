from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth2.client import (OAuth2Client,
														   OAuth2Error)
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialToken, SocialLogin


class OAuth2Adapter(object):

	def get_provider(self):
		return providers.registry.by_id(self.provider_id)

	def complete_login(self, request, app, access_token):
		"""
		Returns a SocialLogin instance
		"""
		raise NotImplementedError

class OAuth2View(object):
	parameters = {}

	@classmethod
	def adapter_view(cls, adapter):
		def view(request, *args, **kwargs):
			self = cls()
			self.request = request
			self.adapter = adapter()
			return self.dispatch(request, *args, **kwargs)
		return view

	def get_client(self, request, app):
		if 'redirect_account_url' in request.GET:
			request.session['redirect_account_url'] = request.GET['redirect_account_url']

		parameters = self.parameters
		for param in request.GET:
			if param.startswith('auth_param_'):
				parameters[param[11:]] = request.GET.get(param)

		callback_url = reverse(self.adapter.provider_id + "_callback")
		callback_url = request.build_absolute_uri(callback_url)
		client = OAuth2Client(self.request, app.key, app.secret,
							  self.adapter.authorize_url,
							  self.adapter.access_token_url,
							  callback_url,
							  self.adapter.get_provider().get_scope(), extra_access_token_post_params=parameters)
		return client


class OAuth2LoginView(OAuth2View):
	def dispatch(self, request):
		app = self.adapter.get_provider().get_app(self.request)
		client = self.get_client(request, app)
		client.state = SocialLogin.marshall_state(request)
		try:
			return HttpResponseRedirect(client.get_redirect_url())
		except OAuth2Error:
			return render_authentication_error(request)


class OAuth2CallbackView(OAuth2View):
	def dispatch(self, request):
		if 'error' in request.GET or not 'code' in request.GET:
			# TODO: Distinguish cancel from error
			return render_authentication_error(request)
		app = self.adapter.get_provider().get_app(self.request)
		client = self.get_client(request, app)
		try:
			access_token, refresh_token = client.get_access_token(request.GET['code'])
			token = SocialToken(app=app,
								token=access_token,
								token_secret=refresh_token)
			login = self.adapter.complete_login(request, app, token)
			token.account = login.account
			login.token = token
			login.state = SocialLogin.unmarshall_state(request.REQUEST
													   .get('state'))
			login.redirect_account_url = request.session.pop('redirect_account_url', None)
			return complete_social_login(request, login)
		except OAuth2Error, e:
			print e
			return render_authentication_error(request)
