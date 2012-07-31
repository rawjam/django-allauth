import django.dispatch


user_logged_in = django.dispatch.Signal(providing_args=["request", "user"])
user_signed_up = django.dispatch.Signal(providing_args=["request", "user"])
