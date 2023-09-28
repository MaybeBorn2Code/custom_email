# Django
from django.dispatch import Signal
from django.core.mail import send_mail
from django.dispatch import receiver

# Local
from settings import base


user_registered = Signal()


@receiver(user_registered)
def user_registered_receiver(sender, **kwargs):
    user = kwargs['user']
    # Sending report to the mail
    send_mail(
        subject='New User Registered',
        message=f'A new user with email {user.email} has registered.',
        from_email=base.EMAIL_HOST_USER,
        recipient_list=['kirillb33@gmail.com'],
        fail_silently=False,
    )
