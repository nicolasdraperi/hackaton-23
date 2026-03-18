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
from .services.ocr import run_ocr


def _mime(doc):
    return {
        '.pdf':  'application/pdf',
        '.jpg':  'image/jpeg', '.jpeg': 'image/jpeg',
        '.png':  'image/png',  '.gif':  'image/gif', '.webp': 'image/webp',
    }.get(doc.extension, 'application/octet-stream')


class BatchListView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = UploadBatch.objects.filter(user=request.user).prefetch_related('documents', 'reviewed_by')
        s = request.query_params.get('status', '')
        if s:
            qs = qs.filter(status=s)
        return Response(UploadBatchSerializer(qs, many=True).data)

    def post(self, request):
        files = request.FILES.getlist('documents')
        label = request.data.get('label', '').strip()
        if not files:
            return Response({'detail': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)
        batch = UploadBatch.objects.create(user=request.user, label=label)
        for f in files:
            Document.objects.create(batch=batch, file=f, original_name=f.name)
        return Response(UploadBatchSerializer(batch).data, status=status.HTTP_201_CREATED)


class DocumentViewFile(APIView):
    def get(self, request, doc_id):
        doc = get_object_or_404(Document, pk=doc_id)
        if not request.user.is_admin_user() and doc.batch.user != request.user:
            raise Http404
        try:
            return FileResponse(doc.file.open('rb'), content_type=_mime(doc))
        except (FileNotFoundError, ValueError):
            raise Http404


class AdminBatchListView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        if not request.user.is_admin_user():
            return Response(status=status.HTTP_403_FORBIDDEN)
        qs = UploadBatch.objects.select_related('user', 'reviewed_by').prefetch_related('documents').order_by('-created_at')
        s = request.query_params.get('status', '')
        u = request.query_params.get('user', '')
        if s:
            qs = qs.filter(status=s)
        if u:
            qs = qs.filter(user__username__icontains=u)
        stats = {
            'pending':  UploadBatch.objects.filter(status='pending').count(),
            'approved': UploadBatch.objects.filter(status='approved').count(),
            'rejected': UploadBatch.objects.filter(status='rejected').count(),
            'users':    User.objects.filter(role='user').count(),
        }
        return Response({'results': UploadBatchSerializer(qs, many=True).data, 'stats': stats})

    def post(self, request):
        if not request.user.is_admin_user():
            return Response(status=status.HTTP_403_FORBIDDEN)
        files = request.FILES.getlist('documents')
        label = request.data.get('label', '').strip()
        user_id = request.data.get('user_id')
        uploader = get_object_or_404(User, pk=user_id) if user_id else request.user
        if not files:
            return Response({'detail': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)
        batch = UploadBatch.objects.create(user=uploader, label=label)
        for f in files:
            Document.objects.create(batch=batch, file=f, original_name=f.name)
        return Response(UploadBatchSerializer(batch).data, status=status.HTTP_201_CREATED)


class AdminBatchApproveView(APIView):
    def post(self, request, batch_id):
        if not request.user.is_admin_user():
            return Response(status=status.HTTP_403_FORBIDDEN)
        batch = get_object_or_404(UploadBatch, pk=batch_id)
        batch.status = 'approved'
        batch.rejection_reason = ''
        batch.reviewed_by = request.user
        batch.reviewed_at = timezone.now()
        batch.save()
        return Response(UploadBatchSerializer(batch).data)


class AdminBatchRejectView(APIView):
    def post(self, request, batch_id):
        if not request.user.is_admin_user():
            return Response(status=status.HTTP_403_FORBIDDEN)
        batch = get_object_or_404(UploadBatch, pk=batch_id)
        batch.status = 'rejected'
        batch.rejection_reason = request.data.get('reason', '').strip()
        batch.reviewed_by = request.user
        batch.reviewed_at = timezone.now()
        batch.save()
        return Response(UploadBatchSerializer(batch).data)
# OCR 
class OCRView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'Aucun fichier fourni.'}, status=400)
        result = run_ocr(file)
        return Response(result)