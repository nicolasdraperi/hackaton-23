from django.db import models
from django.conf import settings
import os


class UploadBatch(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_APPROVED, 'Approuve'),
        (STATUS_REJECTED, 'Refuse'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='batches')
    label = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_batches'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        label = self.label or f'Lot #{self.pk}'
        return f"{label} - {self.user.username} ({self.created_at.strftime('%d/%m/%Y')})"

    @property
    def total(self):
        return self.documents.count()


def upload_path(instance, filename):
    return f'documents/user_{instance.batch.user.id}/{filename}'


class Document(models.Model):
    batch = models.ForeignKey(UploadBatch, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to=upload_path)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return self.original_name

    @property
    def extension(self):
        return os.path.splitext(self.original_name)[1].lower()

    @property
    def is_image(self):
        return self.extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    @property
    def is_pdf(self):
        return self.extension == '.pdf'

    @property
    def file_size_kb(self):
        try:
            return round(self.file.size / 1024, 1)
        except Exception:
            return 0
