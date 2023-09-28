# Python
import os
import bleach
import html
import subprocess

# Django
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.generic import View
from django.http import (
    HttpRequest,
    HttpResponse
)

# Local
from settings import base
from auths.forms import PhotoForm
from abstracts.mixins import HttpResponseMixin
from abstracts.decorators import perfomance_counter
from .forms import (
    PostForm,
    EmailForm
)
from .models import (
    Post,
    Email,
)

# Utils
from .utils import (
    copy_to_excel,
    copy_outbox_to_excel,
    copy_outbox_external_to_excel,
    process_and_save_photo,
    encrypt_caesar,
    decrypt_caesar
)


@method_decorator(cache_page(60 * 2), name='dispatch')
class PostView(LoginRequiredMixin, HttpResponseMixin, View):
    """View special for Post model."""

    form = PostForm

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:

        return self.get_http_response(
            request=request,
            template_name='main\index.html',
            context={
                'ctx_title': 'Mail',
                'ctx_form': self.form()
            }
        )

    @perfomance_counter
    def post(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        form = PostForm(request.POST)

        if request.method == 'POST':
            if form.is_valid():
                current_user = request.user
                recipient = request.POST.get('recipient')
                additional_recipient = request.POST.get(
                    'additional_recipient')
                subject = request.POST.get('subject')
                content = bleach.clean(
                    form.cleaned_data['message'], tags=[], strip=True)
                content = html.unescape(content)
                attach = request.FILES.get('file')

                try:
                    recipients = [recipient]
                    if additional_recipient:
                        recipients.append(additional_recipient)

                    mail = EmailMessage(
                        subject, content, base.EMAIL_HOST_USER, recipients)

                    if attach:
                        mail.attach(attach.name, attach.read(),
                                    attach.content_type)

                    mail.send()

                    mail_model = Post(
                        sender=current_user,
                        recipient=recipient,
                        additional_recipient=additional_recipient,
                        subject=subject,
                        message=content,
                        file=attach if attach else None
                    )
                    mail_model.save()

                    return self.get_http_response(
                        request=request,
                        template_name='main\success_mail.html',
                        context={
                            'ctx_title': 'Mail',
                            'current_user': current_user,
                            'posts': 'and added to outbox'
                        }
                    )

                except Exception as e:
                    return self.get_http_response(
                        request=request,
                        template_name='main\error.html',
                        context={
                            'ctx_title': 'Error',
                        }
                    )

            return self.get_http_response(
                request=request,
                template_name='main\success_mail.html',
                context={
                    'ctx_title': 'Mail',
                    'posts': 'An error'
                }
            )


class PostOutboxView(LoginRequiredMixin, HttpResponseMixin, View):
    """View outbox for Post model."""

    form = PostForm

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        inbox_messages = Post.objects.all()
        # pagination showing 5 messages per page
        messages_per_page = 5
        paginator = Paginator(inbox_messages, messages_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return self.get_http_response(
            request=request,
            template_name='main\main_post.html',
            context={
                'ctx_title': 'Mail Outbox',
                'posts': page_obj
            }
        )

    def post(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        messages = Post.objects.all()
        copy_outbox_external_to_excel(messages)
        return self.get_http_response(
            request=request,
            template_name='main\copy-to-excel-internal.html',
            context={
                'ctx_title': 'Save to Excel',
                'inbox_messages': messages
            }
        )


class OutboxSeachView(LoginRequiredMixin, HttpResponseMixin, View):
    """View for searching emails by keywords."""

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name='main\external_search.html',
            context={
                'ctx_title': 'Search by keyword',
            }
        )

    def post(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        keyword = request.POST.get('keyword')
        sender = request.POST.get('sender')
        recipient = request.POST.get('recipient')
        search_results = Post.objects.search(keyword, sender, recipient)
        return self.get_http_response(
            request=request,
            template_name='main\external_search.html',
            context={
                'ctx_title': 'Search result',
                'search_results': search_results,
                'keyword': keyword,
                'sender': sender,
                'recipient': recipient
            }
        )


@method_decorator(cache_page(60 * 1), name='dispatch')
class EmailView(LoginRequiredMixin, HttpResponseMixin, View):
    """View special for Email model."""

    form = EmailForm

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name='main\internal_index.html',
            context={
                'ctx_title': 'Internal Mail',
                'ctx_form': self.form()
            }
        )

    @perfomance_counter
    def post(self, request: HttpRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        form = EmailForm(request.POST, request.FILES)
        if request.method == "POST" and form.is_valid():
            content = bleach.clean(
                form.cleaned_data['body'], tags=[], strip=True)
            content = html.unescape(content)
            encrypt_content = encrypt_caesar(plaintext=content, shift=3)
            email = form.save(commit=False)
            email.user = request.user
            email.sender = request.user
            email.body = encrypt_content
            email.save()

            recipients = form.cleaned_data['recipients']
            email.recipients.set(recipients)

            return self.get_http_response(
                request=request,
                template_name='main\success_internal_mail.html',
                context={
                    'ctx_title': 'Mail sended',
                    'ctx_form': self.form()
                }
            )
        else:
            form = EmailForm()
        return self.get_http_response(
            request=request,
            template_name='main\error.html',
            context={
                'ctx_title': 'Error',
            }
        )


class SelectEmailView(LoginRequiredMixin, HttpResponseMixin, View):
    """View special to select Email model."""

    form = EmailForm

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name='main\select_mail.html',
            context={
                'ctx_title': 'Select Mail',
                'user': request.user
            }
        )


class SuccessEmailView(LoginRequiredMixin, HttpResponseMixin, View):
    """View special if user sends an email."""

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name='main\success_mail.html',
            context={
                'ctx_title': 'Mail Sended',
            }
        )


class SuccessInternalEmailView(LoginRequiredMixin, HttpResponseMixin, View):
    """View special if user sends an internal email."""

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name='main\success_internal_mail.html',
            context={
                'ctx_title': 'Mail Sended',
            }
        )


class InboxMessagesView(LoginRequiredMixin, HttpResponseMixin, View):
    """Get inbox messages from user."""

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        user = request.user
        inbox_messages = Email.get_inbox_messages(user)
        decrypted_messages = []

        for message in inbox_messages:
            decrypted_body = decrypt_caesar(ciphertext=message.body, shift=3)
            decrypted_messages.append(decrypted_body)

        messages_per_page = 5
        messages_with_decryption = list(
            zip(inbox_messages, decrypted_messages))

        # paginator = Paginator(inbox_messages, messages_per_page)
        paginator = Paginator(messages_with_decryption, messages_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return self.get_http_response(
            request=request,
            template_name='main\internal_inbox.html',
            context={
                'ctx_title': 'Mail Inbox',
                'inbox_messages': page_obj,
                'messages_with_decryption': messages_with_decryption
            }
        )

    def post(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        user = request.user
        inbox_messages = Email.get_inbox_messages(user)
        copy_to_excel(inbox_messages)
        return self.get_http_response(
            request=request,
            template_name='main\copy-to-excel.html',
            context={
                'ctx_title': 'Mail Inbox',
                'inbox_messages': inbox_messages
            }
        )


class OutboxInternalSeachView(LoginRequiredMixin, HttpResponseMixin, View):
    """View for searching emails by keywords."""

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name='main\internal_search.html',
            context={
                'ctx_title': 'Search by keyword',
            }
        )

    def post(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        keyword = request.POST.get('keyword')
        recipients = request.POST.get('recipients')
        current_user_email = request.user.email
        search_results = Email.objects.search(
            keyword, sender=current_user_email, recipients=recipients)
        return self.get_http_response(
            request=request,
            template_name='main\internal_search.html',
            context={
                'ctx_title': 'Search by keyword',
                'search_results': search_results,
                'keyword': keyword,
                'sender': current_user_email,
                'recipients': recipients
            }
        )


class OutboxMessagesView(LoginRequiredMixin, HttpResponseMixin, View):
    """Get outbox messages from user."""

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        user = request.user
        outbox_messages = Email.get_outbox_messages(user)
        decrypted_messages = []
        print(outbox_messages)
        for message in outbox_messages:
            decrypted_body = decrypt_caesar(ciphertext=message.body, shift=3)
            decrypted_messages.append(decrypted_body)

        messages_per_page = 10
        messages_with_decryption = list(
            zip(outbox_messages, decrypted_messages))
        print(messages_with_decryption)

        # paginator = Paginator(outbox_messages, messages_per_page)
        paginator = Paginator(messages_with_decryption, messages_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return self.get_http_response(
            request=request,
            template_name='main\internal_outbox.html',
            context={
                'ctx_title': 'Mail Outbox',
                'outbox_messages': page_obj,
                'messages_with_decryption': messages_with_decryption
            }
        )

    def post(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict
    ) -> HttpResponse:
        user = request.user
        outbox_messages = Email.get_outbox_messages(user)
        copy_outbox_to_excel(outbox_messages)
        return self.get_http_response(
            request=request,
            template_name='main\copy-to-excel-outbox.html',
            context={
                'ctx_title': 'Mail Outbox',
                'inbox_messages': outbox_messages
            }
        )


class EmailDeleteView(LoginRequiredMixin, HttpResponseMixin, View):
    """Deleting outbox messages from user."""

    def post(
        self,
        request: HttpRequest,
        email_id: str,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        email = get_object_or_404(Email, id=email_id)
        email.delete()
        return self.get_http_response(
            request=request,
            template_name='main\delete_email.html',
            context={
                'ctx_title': 'Mail Deleted',
            }
        )


class ChangePhotoView(LoginRequiredMixin, HttpResponseMixin, View):
    """Changing user's photo."""

    def get(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return self.get_http_response(
            request=request,
            template_name='main\photo_change.html',
            context={
                'ctx_title': 'Change photo',
            }
        )

    def post(
        self,
        request: HttpRequest,
        email_id: str,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data['photo']
            photo_file = process_and_save_photo(photo)
            user = Email.get_user_by_email(email_id)
            user.photo.save(photo.name, photo_file, save=True)
            return self.get_http_response(
                request=request,
                template_name='main\photo_change.html',
                context={
                    'ctx_title': 'Change photo',
                    'form': form,
                    'info': "Photo updated successfully"
                }
            )
        return self.get_http_response(
            request=request,
            template_name='main\photo_change.html',
            context={
                'ctx_title': 'Change photo',
                'form': form,
                'info': "An error occured, please check image size and format (JPG, PNG...)"
            }
        )
