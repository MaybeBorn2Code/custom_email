# Django
from django.db import models
from django.db.models import Q

# Local
from auths.models import CustomUser


class PostManager(models.Manager):
    def search(self, keyword, sender=None, recipient=None):
        queryset = self.get_queryset()
        if keyword:
            queryset = queryset.filter(
                Q(message__icontains=keyword) |
                Q(subject__icontains=keyword)
            )
        if sender:
            queryset = queryset.filter(sender__email__icontains=sender)
        if recipient:
            queryset = queryset.filter(
                Q(recipient__icontains=recipient) |
                Q(additional_recipient__icontains=recipient)
            )
        return queryset


class Post(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipient = models.EmailField()
    additional_recipient = models.EmailField(blank=True)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    file = models.FileField(
        verbose_name="file",
        upload_to="media/",
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PostManager()

    @classmethod
    def get_inbox_messages(cls, user):
        return cls.objects.filter(recipient=user)

    class Meta:
        ordering = (
            "-id",
        )
        verbose_name = "mail"
        verbose_name_plural = "mails"

    def __str__(self) -> str:
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"Sender: {self.sender}, Recipient: {self.recipient}, Additional Recipient: {self.additional_recipient}, Subject: {self.subject}, Message: {self.message}, Time: {timestamp_str}"


class EmailManager(models.Manager):
    def search(self, keyword, sender=None, recipients=None):
        queryset = self.get_queryset()
        if keyword:
            queryset = queryset.filter(
                Q(body__icontains=keyword) |
                Q(subject__icontains=keyword)
            )
        if sender:
            queryset = queryset.filter(sender__email__icontains=sender)
        if recipients:
            queryset = queryset.filter(recipients__email__icontains=recipients)
        return queryset


class Email(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name="emails_sent")
    recipients = models.ManyToManyField(
        CustomUser, related_name="emails_received")
    subject = models.CharField(max_length=100)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(
        upload_to="email_attachments/", blank=True, null=True)
    deleted_by = models.ManyToManyField(
        CustomUser, blank=True, related_name="deleted_emails")

    objects = EmailManager()

    @staticmethod
    def get_user_by_email(email):
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None

    @classmethod
    def get_inbox_messages(cls, user):
        return cls.objects.filter(recipients=user).exclude(deleted_by=user)

    @classmethod
    def get_outbox_messages(cls, user):
        return cls.objects.filter(sender=user).exclude(deleted_by=user)

    class Meta:
        ordering = (
            "-id",
        )
        verbose_name = "internal_mail"
        verbose_name_plural = "internal_mails"

    def __str__(self):
        sender = self.sender.email if self.sender else "Unknown"
        recipients = ", ".join(
            [user.email for user in self.recipients.all()])
        return f"Sender: {sender}, Recipients: {recipients}, Subject: {self.subject}"
