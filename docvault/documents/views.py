from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, Http404
from .models import UploadBatch, Document
from accounts.models import User
import os

from django.http import JsonResponse
from .mongo import documents_collection
from datetime import datetime
from django.conf import settings
from bson import ObjectId



@login_required
def upload_view(request):
    if request.method == 'POST':
        files = request.FILES.getlist('documents')
        label = request.POST.get('label', '').strip()

        if not files:
            messages.error(request, "Veuillez selectionner au moins un fichier.")
            return redirect('upload_documents')

        documents_data = []

        for f in files:
            path = f"documents/user_{request.user.id}/{f.name}"
            full_path = os.path.join(settings.MEDIA_ROOT, path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            documents_data.append({
                "original_name": f.name,
                "file_path": path,
                "uploaded_at": datetime.now(),
                "extension": os.path.splitext(f.name)[1].lower(),
                "size_kb": round(f.size / 1024, 1)
            })

        batch = {
            "user_id": request.user.id,
            "label": label,
            "status": "pending",
            "rejection_reason": "",
            "created_at": datetime.now(),
            "reviewed_at": None,
            "reviewed_by": None,
            "documents": documents_data
        }

        result = documents_collection.insert_one(batch)
        print("INSERTED ID:", result.inserted_id)

        messages.success(request, f"{len(files)} document(s) uploadés.")
        return redirect('my_documents')

    return render(request, 'documents/upload.html')

@login_required
def my_documents_view(request):
    status_filter = request.GET.get('status', '')

    query = {"user_id": request.user.id}
    if status_filter:
        query["status"] = status_filter

    batches = list(documents_collection.find(query))

    for b in batches:
        b["_id"] = str(b["_id"])

    return render(request, 'documents/my_documents.html', {
        'batches': batches,
        'status_filter': status_filter,
    })


@login_required
def view_document(request, batch_id, doc_index):
    batch = documents_collection.find_one({"_id": ObjectId(batch_id)})

    if not batch:
        raise Http404

    if not request.user.is_admin_user() and batch["user_id"] != request.user.id:
        raise Http404

    try:
        doc = batch["documents"][int(doc_index)]
    except:
        raise Http404

    file_path = os.path.join(settings.MEDIA_ROOT, doc["file_path"])

    if not os.path.exists(file_path):
        raise Http404

    return FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')


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

    pending_batches = list(documents_collection.find({"status": "pending"}).sort("created_at", -1).limit(10))

    total_pending = documents_collection.count_documents({"status": "pending"})
    total_approved = documents_collection.count_documents({"status": "approved"})
    total_rejected = documents_collection.count_documents({"status": "rejected"})
    total_users = User.objects.filter(role='user').count()

    for b in pending_batches:
        b["_id"] = str(b["_id"])

    return render(request, 'admin/dashboard.html', {
        'pending_batches': pending_batches,
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

    query = {}

    if status_filter:
        query["status"] = status_filter

    batches = list(documents_collection.find(query).sort("created_at", -1))

    if user_filter:
        users = User.objects.filter(username__icontains=user_filter)
        user_ids = [u.id for u in users]
        batches = [b for b in batches if b["user_id"] in user_ids]

    for b in batches:
        b["_id"] = str(b["_id"])

    return render(request, 'admin/review.html', {
        'batches': batches,
        'status_filter': status_filter,
        'user_filter': user_filter,
    })


@login_required
def admin_approve_batch(request, batch_id):
    if not request.user.is_admin_user():
        return redirect('user_profile')

    documents_collection.update_one(
        {"_id": ObjectId(batch_id)},
        {"$set": {
            "status": "approved",
            "rejection_reason": "",
            "reviewed_by": request.user.id,
            "reviewed_at": datetime.now()
        }}
    )

    messages.success(request, "Lot approuvé.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_review'))


@login_required
def admin_reject_batch(request, batch_id):
    if not request.user.is_admin_user():
        return redirect('user_profile')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()

        documents_collection.update_one(
            {"_id": ObjectId(batch_id)},
            {"$set": {
                "status": "rejected",
                "rejection_reason": reason,
                "reviewed_by": request.user.id,
                "reviewed_at": datetime.now()
            }}
        )

        messages.warning(request, "Lot refusé.")
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
            documents_data = []

            for f in files:
                path = f"documents/user_{uploader.id}/{f.name}"
                full_path = os.path.join(settings.MEDIA_ROOT, path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)

                documents_data.append({
                    "original_name": f.name,
                    "file_path": path,
                    "uploaded_at": datetime.now(),
                    "extension": os.path.splitext(f.name)[1].lower(),
                    "size_kb": round(f.size / 1024, 1)
                })

            documents_collection.insert_one({
                "user_id": uploader.id,
                "label": label,
                "status": "pending",
                "rejection_reason": "",
                "created_at": datetime.now(),
                "reviewed_at": None,
                "reviewed_by": None,
                "documents": documents_data
            })

            messages.success(request, f"{len(files)} document(s) uploadés.")
            return redirect('admin_review')

    users = User.objects.all().order_by('username')
    return render(request, 'admin/upload.html', {'users': users})