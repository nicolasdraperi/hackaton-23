from django.urls import path
from . import views

urlpatterns = [
    path('documents/upload/', views.upload_view, name='upload_documents'),
    path('documents/mes-documents/', views.my_documents_view, name='my_documents'),
    path('documents/<int:doc_id>/view/', views.view_document, name='view_document'),
    path('gestion/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('gestion/review/', views.admin_review_view, name='admin_review'),
    path('gestion/review/<int:batch_id>/approve/', views.admin_approve_batch, name='admin_approve'),
    path('gestion/review/<int:batch_id>/reject/', views.admin_reject_batch, name='admin_reject'),
    path('gestion/upload/', views.admin_upload_view, name='admin_upload'),
]
