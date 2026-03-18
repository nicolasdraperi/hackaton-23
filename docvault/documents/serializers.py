from rest_framework import serializers
from .models import UploadBatch, Document


class DocumentSerializer(serializers.ModelSerializer):
    extension   = serializers.ReadOnlyField()
    is_image    = serializers.ReadOnlyField()
    is_pdf      = serializers.ReadOnlyField()
    file_size_kb = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = ['id', 'original_name', 'file', 'extension',
                  'is_image', 'is_pdf', 'file_size_kb', 'uploaded_at']
        read_only_fields = fields


class UploadBatchSerializer(serializers.ModelSerializer):
    documents    = DocumentSerializer(many=True, read_only=True)
    user         = serializers.SerializerMethodField()
    reviewed_by  = serializers.SerializerMethodField()
    total        = serializers.ReadOnlyField()

    class Meta:
        model = UploadBatch
        fields = [
            'id', 'label', 'status', 'rejection_reason',
            'user', 'reviewed_by', 'reviewed_at', 'created_at',
            'documents', 'total',
        ]
        read_only_fields = fields

    def get_user(self, obj):
        u = obj.user
        return {
            'id': u.id,
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
        }

    def get_reviewed_by(self, obj):
        if obj.reviewed_by:
            return {'id': obj.reviewed_by.id, 'username': obj.reviewed_by.username}
        return None
