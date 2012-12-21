from django.dispatch import Signal

user_logged_in = Signal(providing_args=["request", "user"])
user_signed_up = Signal(providing_args=["request", "user"])


# Sent after a user successfully authenticates via a social provider,
# but before the login is actually processed. This signal is emitted
# for social logins, signups and when connecting additional social
# accounts to an account.
pre_social_login = Signal(providing_args=["request", "sociallogin"])