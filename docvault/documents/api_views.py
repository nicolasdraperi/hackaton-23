from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import UploadBatch, Document
from .serializers import UploadBatchSerializer
from accounts.models import User
from bson import ObjectId
from .mongo import documents_collection
from datetime import datetime
import os
from django.conf import settings



def _mime(doc):
    return {
        '.pdf':  'application/pdf',
        '.jpg':  'image/jpeg', '.jpeg': 'image/jpeg',
        '.png':  'image/png',  '.gif':  'image/gif', '.webp': 'image/webp',
    }.get(doc.extension, 'application/octet-stream')



class BatchListView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        query = {"user_id": request.user.id}
        s = request.query_params.get('status', '')
        if s:
            query["status"] = s

        batches = list(documents_collection.find(query))

        for b in batches:
            b["_id"] = str(b["_id"])

        return Response(batches)

    def post(self, request):
        files = request.FILES.getlist('documents')
        label = request.data.get('label', '').strip()

        if not files:
            return Response({'detail': 'Aucun fichier fourni.'}, status=400)

        documents_data = []

        for f in files:
            path = f"documents/user_{request.user.id}/{f.name}"
            full_path = os.path.join(settings.MEDIA_ROOT, path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)

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

        batch["_id"] = str(result.inserted_id)

        return Response(batch, status=201)

class DocumentViewFile(APIView):
    def get(self, request, batch_id, doc_index):
        batch = documents_collection.find_one({"_id": ObjectId(batch_id)})

        if not batch:
            raise Http404

        # sécurité
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


class AdminBatchListView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        if not request.user.is_admin_user():
            return Response(status=403)

        s = request.query_params.get('status', '')
        u = request.query_params.get('user', '')

        query = {}
        if s:
            query["status"] = s

        batches = list(documents_collection.find(query).sort("created_at", -1))

        if u:
            users = User.objects.filter(username__icontains=u)
            ids = [user.id for user in users]
            batches = [b for b in batches if b["user_id"] in ids]

        stats = {
            'pending': documents_collection.count_documents({"status": "pending"}),
            'approved': documents_collection.count_documents({"status": "approved"}),
            'rejected': documents_collection.count_documents({"status": "rejected"}),
            'users': User.objects.filter(role='user').count(),
        }

        for b in batches:
            b["_id"] = str(b["_id"])

        return Response({'results': batches, 'stats': stats})

    def post(self, request):
        if not request.user.is_admin_user():
            return Response(status=403)

        files = request.FILES.getlist('documents')
        label = request.data.get('label', '').strip()
        user_id = request.data.get('user_id')

        uploader = request.user
        if user_id:
            uploader = get_object_or_404(User, pk=user_id)

        if not files:
            return Response({'detail': 'Aucun fichier fourni.'}, status=400)

        documents_data = []

        for f in files:
            path = f"documents/user_{uploader.id}/{f.name}"
            full_path = os.path.join(settings.MEDIA_ROOT, path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)

            documents_data.append({
                "original_name": f.name,
                "file_path": path,
                "uploaded_at": datetime.now(),
                "extension": os.path.splitext(f.name)[1].lower(),
                "size_kb": round(f.size / 1024, 1)
            })

        batch = {
            "user_id": uploader.id,
            "label": label,
            "status": "pending",
            "rejection_reason": "",
            "created_at": datetime.now(),
            "reviewed_at": None,
            "reviewed_by": None,
            "documents": documents_data
        }

        result = documents_collection.insert_one(batch)
        batch["_id"] = str(result.inserted_id)

        return Response(batch, status=201)



class AdminBatchApproveView(APIView):
    def post(self, request, batch_id):
        if not request.user.is_admin_user():
            return Response(status=403)

        documents_collection.update_one(
            {"_id": ObjectId(batch_id)},
            {"$set": {
                "status": "approved",
                "rejection_reason": "",
                "reviewed_by": request.user.id,
                "reviewed_at": datetime.now()
            }}
        )

        return Response({"message": "approved"})


class AdminBatchRejectView(APIView):
    def post(self, request, batch_id):
        if not request.user.is_admin_user():
            return Response(status=403)

        documents_collection.update_one(
            {"_id": ObjectId(batch_id)},
            {"$set": {
                "status": "rejected",
                "rejection_reason": request.data.get('reason', ''),
                "reviewed_by": request.user.id,
                "reviewed_at": datetime.now()
            }}
        )

        return Response({"message": "rejected"})
