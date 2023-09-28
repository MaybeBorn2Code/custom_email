# DRF
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    path
)
from django.contrib.auth import views as auth_views

# Local
from main.views import (
    PostView,
    PostOutboxView,
    EmailView,
    SelectEmailView,
    SuccessEmailView,
    SuccessInternalEmailView,
    InboxMessagesView,
    OutboxMessagesView,
    EmailDeleteView,
    ChangePhotoView,
    OutboxSeachView,
    OutboxInternalSeachView
)
from auths.views import (
    RegistrationView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    DefaultPasswordView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(), name='login'),
    path('mail/', PostView.as_view(), name='mail'),
    path('select/', SelectEmailView.as_view(), name='select'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('external_outbox/', PostOutboxView.as_view(), name='archive'),
    path('external_search/', OutboxSeachView.as_view(), name='external_search'),
    path('success_mail', SuccessEmailView.as_view(), name='success_mail'),
    path('success_internal_mail', SuccessInternalEmailView.as_view(),
         name='success_internal_mail'),
    path('internal/', EmailView.as_view(), name='internal_mail'),
    path('inbox/', InboxMessagesView.as_view(), name='internal_inbox'),
    path('inbox_search/', OutboxInternalSeachView.as_view(), name='internal_search'),
    path('outbox/', OutboxMessagesView.as_view(), name='internal_outbox'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('copy-to-excel/', InboxMessagesView.as_view(), name='copy-to-excel'),
    path('copy-to-excel-outbox/', OutboxMessagesView.as_view(),
         name='copy-to-excel-outbox'),
    path('copy-to-excel-internal/', PostOutboxView.as_view(),
         name='copy-to-excel-internal'),
    path('email/<int:email_id>/delete/',
         EmailDeleteView.as_view(), name='delete_email'),
    path('change_photo/<str:email_id>/',
         ChangePhotoView.as_view(), name='change_photo'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('default_password/', DefaultPasswordView.as_view(),
         name='default_password'),
    path('summernote/', include('django_summernote.urls')),


] + static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
) + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]


urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
