# Python
from PIL import Image

# Django
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.exceptions import ValidationError
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom user manager class."""

    def create_user(
        self,
        email: str,
        password: str
    ) -> 'CustomUser':

        if not email:
            raise ValidationError("Email is none!")

        custom_user: 'CustomUser' = self.model(
            email=self.normalize_email(email),
            password=password
        )
        custom_user.set_password(password)
        custom_user.save(using=self._db)
        return custom_user

    def create_superuser(
        self,
        email: str,
        password: str
    ) -> 'CustomUser':

        if not email:
            raise ValidationError("Email is none!")

        custom_user: 'CustomUser' = self.model(
            email=self.normalize_email(email),
            password=password
        )
        custom_user.is_staff = True
        custom_user.is_superuser = True
        custom_user.set_password(password)
        custom_user.save(using=self._db)
        return custom_user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """My custom user."""

    email = models.EmailField(
        max_length=100, unique=True, verbose_name='почта'
    )
    is_active = models.BooleanField(
        default=True, verbose_name='активность'
    )
    is_superuser = models.BooleanField(
        default=True, verbose_name='администратор'
    )
    is_staff = models.BooleanField(
        default=True, verbose_name='менеджер'
    )
    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name='дата регистрации'
    )
    photo = models.ImageField(verbose_name="photo")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        ordering = (
            '-id',
        )
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.photo:
            img = Image.open(self.photo.path)

            if img.mode == 'RGBA':
                img = img.convert('RGB')

            if img.height > 300 and img.width > 300:
                output_size = (150, 150)
                img.thumbnail(output_size)
                img.save(self.photo.path, 'JPEG')
