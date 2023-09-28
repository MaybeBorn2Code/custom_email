# Django
from django.forms import (
    Form,
    PasswordInput,
    CharField,
    EmailField
)
from django import forms
from django.contrib.auth.forms import UserCreationForm

# Local
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """Registration form for CustomUser."""

    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')


class LoginForm(Form):
    """Login form for CustomUser."""

    email = EmailField(
        label='Почта',
        max_length=50
    )
    password = CharField(
        label='Пароль',
        max_length=20,
        min_length=8,
        widget=PasswordInput()
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'password',
        )


class PhotoForm(forms.Form):
    photo = forms.ImageField(label='Photo')
