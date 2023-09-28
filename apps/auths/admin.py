# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Local
from auths.models import CustomUser


class ClientAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        ('Information', {
            'fields': (
                'email',
                'password',
                'date_joined',
                'photo'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_superuser',
                'is_staff',
                'is_active',
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': (
                'wide',
            ),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_active'
            ),
        }),
    )
    search_fields = (
        'email',
    )
    readonly_fields = (
        'date_joined',
        'is_superuser',
        'is_staff',
        'is_active'
    )
    list_filter = (
        'email',
        'is_superuser',
        'is_staff',
        'is_active'
    )
    list_display = [
        'email',
        'password',
        'date_joined',
        'is_superuser',
        'is_staff',
        'is_active',
        'photo'
    ]
    ordering = (
        'email',
    )


admin.site.register(CustomUser, ClientAdmin)
