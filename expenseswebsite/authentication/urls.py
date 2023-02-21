from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import EmailValidationView, RegistrationView, UsernameValidationView

urlpatterns = [
    path("register", RegistrationView.as_view(), name="register"),
    path(
        "validate-username",
        csrf_exempt(UsernameValidationView.as_view()),
        name="validate-username",
    ),
    path(
        "validate-email",
        csrf_exempt(EmailValidationView.as_view()),
        name="validate-email",
    ),
]
