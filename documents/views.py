from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, Http404
from .models import UploadBatch, Document
from accounts.models import User
import os


@login_required
def upload_view(request):
    if request.method == 'POST':
        files = request.FILES.getlist('documents')
        label = request.POST.get('label', '').strip()
        if not files:
            messages.error(request, "Veuillez selectionner au moins un fichier.")
            return redirect('upload_documents')
        batch = UploadBatch.objects.create(user=request.user, label=label)
        for f in files:
            Document.objects.create(batch=batch, file=f, original_name=f.name)
        messages.success(request, f"{len(files)} document(s) uploade(s) dans le lot #{batch.pk}.")
        return redirect('my_documents')
    return render(request, 'documents/upload.html')


@login_required
def my_documents_view(request):
    status_filter = request.GET.get('status', '')
    batches = UploadBatch.objects.filter(user=request.user).prefetch_related('documents')
    if status_filter:
        batches = batches.filter(status=status_filter)
    return render(request, 'documents/my_documents.html', {
        'batches': batches,
        'status_filter': status_filter,
    })


@login_required
def view_document(request, doc_id):
    doc = get_object_or_404(Document, pk=doc_id)
    # User can only view their own docs; admins can view all
    if not request.user.is_admin_user() and doc.batch.user != request.user:
        raise Http404
    if not doc.file:
        raise Http404
    try:
        return FileResponse(doc.file.open('rb'), content_type=_content_type(doc))
    except FileNotFoundError:
        raise Http404


def _content_type(doc):
    ext = doc.extension
    mapping = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp',
    }
    return mapping.get(ext, 'application/octet-stream')


@login_required
def admin_dashboard_view(request):
    if not request.user.is_admin_user():
        return redirect('user_profile')
    pending_batches = UploadBatch.objects.filter(status='pending').select_related('user').prefetch_related('documents')
    total_pending = UploadBatch.objects.filter(status='pending').count()
    total_approved = UploadBatch.objects.filter(status='approved').count()
    total_rejected = UploadBatch.objects.filter(status='rejected').count()
    total_users = User.objects.filter(role='user').count()
    return render(request, 'admin/dashboard.html', {
        'pending_batches': pending_batches[:10],
        'total_pending': total_pending,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
        'total_users': total_users,
    })


@login_required
def admin_review_view(request):
    if not request.user.is_admin_user():
        return redirect('user_profile')
    status_filter = request.GET.get('status', 'pending')
    user_filter = request.GET.get('user', '')
    batches = UploadBatch.objects.select_related('user', 'reviewed_by').prefetch_related('documents').order_by('-created_at')
    if status_filter:
        batches = batches.filter(status=status_filter)
    if user_filter:
        batches = batches.filter(user__username__icontains=user_filter)
    return render(request, 'admin/review.html', {
        'batches': batches,
        'status_filter': status_filter,
        'user_filter': user_filter,
    })


@login_required
def admin_approve_batch(request, batch_id):
    if not request.user.is_admin_user():
        return redirect('user_profile')
    batch = get_object_or_404(UploadBatch, pk=batch_id)
    batch.status = 'approved'
    batch.rejection_reason = ''
    batch.reviewed_by = request.user
    batch.reviewed_at = timezone.now()
    batch.save()
    label = batch.label or f'Lot #{batch.pk}'
    messages.success(request, f"Lot \"{label}\" approuve.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_review'))


@login_required
def admin_reject_batch(request, batch_id):
    if not request.user.is_admin_user():
        return redirect('user_profile')
    if request.method == 'POST':
        batch = get_object_or_404(UploadBatch, pk=batch_id)
        reason = request.POST.get('reason', '').strip()
        batch.status = 'rejected'
        batch.rejection_reason = reason
        batch.reviewed_by = request.user
        batch.reviewed_at = timezone.now()
        batch.save()
        label = batch.label or f'Lot #{batch.pk}'
        messages.warning(request, f"Lot \"{label}\" refuse.")
        return redirect(request.META.get('HTTP_REFERER', 'admin_review'))
    return redirect('admin_review')


@login_required
def admin_upload_view(request):
    if not request.user.is_admin_user():
        return redirect('user_profile')
    if request.method == 'POST':
        files = request.FILES.getlist('documents')
        label = request.POST.get('label', '').strip()
        user_id = request.POST.get('user_id')
        uploader = request.user
        if user_id:
            uploader = get_object_or_404(User, pk=user_id)
        if not files:
            messages.error(request, "Veuillez selectionner au moins un fichier.")
        else:
            batch = UploadBatch.objects.create(user=uploader, label=label)
            for f in files:
                Document.objects.create(batch=batch, file=f, original_name=f.name)
            messages.success(request, f"{len(files)} document(s) uploade(s) pour {uploader.username}.")
            return redirect('admin_review')
    users = User.objects.all().order_by('username')
    return render(request, 'admin/upload.html', {'users': users})
