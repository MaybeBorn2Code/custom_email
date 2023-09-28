# Django
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

# Local
from .models import (
    Post,
    Email
)


class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('message',)


class EmailAdmin(SummernoteModelAdmin):
    summernote_fields = ('body',)


admin.site.register(Post, PostAdmin)
admin.site.register(Email, EmailAdmin)
