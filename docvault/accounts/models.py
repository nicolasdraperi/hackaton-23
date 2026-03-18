from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_USER, 'Utilisateur'),
        (ROLE_ADMIN, 'Administrateur'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
