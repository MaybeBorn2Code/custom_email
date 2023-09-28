# Django
from django.views.generic import View
from django.forms.models import ModelFormMetaclass
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib.auth.tokens import default_token_generator
from django.utils.crypto import get_random_string
from django.http import (
    HttpRequest,
    HttpResponse
)
from django.contrib.auth import (
    login,
    logout,
    authenticate
)

# Local
from .models import CustomUser
from abstracts.mixins import HttpResponseMixin
from auths.forms import (
    RegistrationForm,
    LoginForm
)

# Utils
from .utils import save_password_to_file
from .signals import user_registered


class RegistrationView(HttpResponseMixin, View):
    """Registration View."""

    template_name = 'auths/registration.html'
    form: ModelFormMetaclass = RegistrationForm

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name=self.template_name,
            context={
                'ctx_title': 'Registration',
                'ctx_form': self.form()
            }
        )

    def post(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        form = self.form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            password_confirmation = form.cleaned_data['password2']

            if password != password_confirmation:
                return self.get_http_response(
                    request=request,
                    template_name=self.template_name,
                    context={
                        'ctx_title': 'Registration',
                        'ctx_form': self.form(),
                        'info': 'Passwords do not match'
                    }
                )
            try:
                user = form.save(commit=False)
                user.set_password(password)
                user.save()
            except IntegrityError:
                return self.get_http_response(
                    request=request,
                    template_name=self.template_name,
                    context={
                        'ctx_title': 'Registration',
                        'ctx_form': self.form(),
                        'info': 'User already exists'
                    }
                )
            # signal
            user_registered.send(sender=self.__class__, user=user)
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    'ctx_title': 'Registration',
                    'ctx_form': self.form(),
                    'info': 'User successfully created'
                }
            )
        else:
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    'ctx_title': 'Registration',
                    'ctx_form': self.form(),
                    'info': 'Please check your password, choose another email'
                }
            )


class LoginView(HttpResponseMixin, View):
    """Login View."""

    template_name: str = 'auths/login.html'
    form: ModelFormMetaclass = LoginForm

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name=self.template_name,
            context={
                'ctx_title': 'Login',
                'ctx_form': self.form()
            }
        )

    def post(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        form: LoginForm = self.form(
            request.POST
        )
        if not form.is_valid():
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    'ctx_title': 'Login',
                    'ctx_form': form
                }
            )

        email = request.POST['email']
        password = request.POST['password']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    'ctx_title': 'Login',
                    'error': 'User does not exist in database, please create an account'
                }
            )
        else:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                token = default_token_generator.make_token(user)
                access_token = token
                print(access_token)
                response = redirect('/select')
                response.set_cookie('access_token', access_token)
                return response
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    'ctx_title': 'Login',
                    'error': 'Password is not correct'
                }
            )


class LogoutView(HttpResponseMixin, View):
    """LogoutView."""

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        if request.user:
            logout(request)

        return redirect('/')


class ChangePasswordView(HttpResponseMixin, View):
    """View to change user password."""

    template_name: str = "auths/change_password.html"

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:

        return self.get_http_response(
            request=request,
            template_name=self.template_name,
            context={
                "ctx_user": request.user
            }
        )

    def post(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        old_password = request.POST.get('pass')
        new_password = request.POST.get('pass2')
        if len(new_password) < 8 or len(new_password) > 20:
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    "info": 'Please enter a password between 8 and 20 characters long'
                }
            )
        user = authenticate(
            username=request.user.email,
            password=old_password
        )
        if not user:
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    "info": 'Please check user credentials and try enter password again'
                }
            )
        user.set_password(new_password)
        user.save(update_fields=('password',))
        return self.get_http_response(
            request=request,
            template_name=self.template_name,
            context={
                "ctx_user": request.user,
                'info': 'Password changed successfully'
            }
        )


class DefaultPasswordView(HttpResponseMixin, View):
    """View to change user password to default."""

    template_name: str = "auths/default_password.html"

    def get(
        self,
        request: WSGIRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:

        return self.get_http_response(
            request=request,
            template_name=self.template_name,
            context={
                "ctx_user": request.user
            }
        )

    def post(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        if request.method == 'POST':
            email = request.POST['email']
            try:
                user = CustomUser.objects.get(email=email)
                new_password = get_random_string(length=10)
                user.set_password(new_password)
                user.save()
                save_password_to_file(email, new_password)
                return self.get_http_response(
                    request=request,
                    template_name=self.template_name,
                    context={
                        "ctx_user": request.user,
                        "info": "Password changed successfully"
                    }
                )
            except CustomUser.DoesNotExist:
                return self.get_http_response(
                    request=request,
                    template_name=self.template_name,
                    context={
                        "ctx_user": request.user,
                        "info": "Email not found"
                    }
                )
        else:
            return self.get_http_response(
                request=request,
                template_name=self.template_name,
                context={
                    "ctx_user": request.user
                }
            )
