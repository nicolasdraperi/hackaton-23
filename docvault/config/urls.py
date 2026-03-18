from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.api_views import (
    csrf_view, login_view, logout_view, register_view,
    MeView, AdminUsersView, AdminUserDetailView,
)
from documents.api_views import (
    BatchListView, DocumentViewFile,
    AdminBatchListView, AdminBatchApproveView, AdminBatchRejectView,
)
from documents.api_views import OCRView


api = [
    path('auth/csrf/',              csrf_view),
    path('auth/login/',             login_view),
    path('auth/logout/',            logout_view),
    path('auth/register/',          register_view),
    path('auth/me/',                MeView.as_view()),

    path('batches/',                BatchListView.as_view()),
    path('documents/<int:doc_id>/view/', DocumentViewFile.as_view()),

    path('admin/batches/',                          AdminBatchListView.as_view()),
    path('admin/batches/<int:batch_id>/approve/',   AdminBatchApproveView.as_view()),
    path('admin/batches/<int:batch_id>/reject/',    AdminBatchRejectView.as_view()),
    path('admin/users/',                            AdminUsersView.as_view()),
    path('admin/users/<int:user_id>/',              AdminUserDetailView.as_view()),

    path('documents/ocr/', OCRView.as_view()),

]

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include(api)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
