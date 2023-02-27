from email import message
import re
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
import json
from django.urls import reverse
from validate_email import validate_email
from django.http import JsonResponse

from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages

from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import auth

from .utils import token_gen

# Create your views here.


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data["username"]

        if not str(username).isalnum():
            return JsonResponse(
                {
                    "username_error": "username should only contain alphanumeric characters"
                },
                status=400,
            )
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"username_error": "sorry username in use, choose another one"},
                status=409,
            )
        return JsonResponse({"username_valid": True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data["email"]

        if not validate_email(email):
            return JsonResponse(
                {"email_error": "email is invalid"},
                status=400,
            )
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"email_error": "sorry email in use, choose another one"},
                status=409,
            )
        return JsonResponse({"email_valid": True})


class RegistrationView(View):
    def get(self, request):
        return render(request, "authentication/register.html")

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # CREATE USER ACCOUNT

        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]

        context = {"fieldValues": request.POST}

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password too short")
                    return render(request, "authentication/register.html", context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                email_subject = "Activate your account"
                #  PATH TO VIEW
                # GET DOMAIN WE ARE ON
                # RELATIVE URL VERTIFICATION
                # ENCODE UID
                # TOKEN
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain
                link = reverse(
                    "activate",
                    kwargs={"uidb64": uidb64, "token": token_gen.make_token(user)},
                )

                email_body = f"Hi {user.username} Please use this link to verify your account\n http://{domain}{link}"

                email = EmailMessage(
                    email_subject,
                    email_body,
                    "noreply@semycolon.com",
                    [email],
                )
                email.send(fail_silently=True)
                messages.success(request, "Account successfully created")
                return render(request, "authentication/register.html")

        return render(request, "authentication/register.html")


class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_gen.check_token(user, token=token):
                return redirect("login" + "?message=" + "User already activated")

            if user.is_active:
                return redirect("login")
            user.is_active = True
            user.save()

            messages.success(request, "Account activated successfully")
            return redirect("login")
        except Exception as e:
            pass

        return redirect("login")


class LoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(
                        request, f"Welcome, {user.username} you are now logged in!"
                    )
                    return redirect("expenses")
                messages.error(request, "Account is not active, please check email")
                return render(request, "authentication/login.html")
            messages.error(request, "Invalid credentials,  try again")
            return render(request, "authentication/login.html")

        messages.error(request, "Please fill all fields")
        return render(request, "authentication/login.html")


class LogoutView(View):
    def post(self, request):
        auth.logout(request)

        messages.success(request, "You have been logged out")
        return redirect("login")
