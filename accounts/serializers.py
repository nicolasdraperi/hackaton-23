from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    batches_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone', 'bio', 'avatar', 'role', 'is_superuser',
            'date_joined', 'batches_count',
        ]
        read_only_fields = ['id', 'username', 'is_superuser', 'date_joined', 'batches_count']

    def get_batches_count(self, obj):
        return obj.batches.count()


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Les mots de passe ne correspondent pas.'})
        validate_password(data['password1'])
        return data

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        return User.objects.create_user(password=password, **validated_data)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
