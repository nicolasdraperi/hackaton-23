from django.contrib import admin
from .models import UploadBatch, Document

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(UploadBatch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'label', 'status', 'created_at']
    list_filter = ['status']
    inlines = [DocumentInline]

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'batch', 'uploaded_at']
