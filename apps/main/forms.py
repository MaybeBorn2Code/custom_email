# Django
from django import forms
from django.shortcuts import render
from django_summernote.widgets import SummernoteWidget

# Local
from main.models import (
    Post,
    Email
)
from main.models import CustomUser


class PostForm(forms.ModelForm):
    """Post form."""

    message = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = Post
        fields = [
            'recipient',
            'additional_recipient',
            'subject',
            'message',
            'file'
        ]


class EmailForm(forms.ModelForm):
    """Email form."""

    recipients = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = Email
        fields = [
            'recipients',
            'subject',
            'body',
            'attachment'
        ]
        widgets = {'body': SummernoteWidget()}
