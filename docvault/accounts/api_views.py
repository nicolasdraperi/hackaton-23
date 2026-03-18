from django.contrib.auth import login, logout, authenticate
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from django.db.models import Q
from .models import User
from .serializers import UserSerializer, RegisterSerializer, RoleSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_view(request):
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({'user': UserSerializer(user).data})
    return Response({'detail': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'detail': 'Deconnecte.'})


class MeView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUsersView(APIView):
    def get(self, request):
        if not request.user.is_admin_user():
            return Response(status=status.HTTP_403_FORBIDDEN)
        q = request.query_params.get('q', '')
        users = User.objects.all().order_by('username')
        if q:
            users = users.filter(
                Q(username__icontains=q) | Q(email__icontains=q) |
                Q(first_name__icontains=q) | Q(last_name__icontains=q)
            )
        return Response(UserSerializer(users, many=True).data)


class AdminUserDetailView(APIView):
    def patch(self, request, user_id):
        if not request.user.is_admin_user():
            return Response(status=status.HTTP_403_FORBIDDEN)
        from django.shortcuts import get_object_or_404
        user = get_object_or_404(User, pk=user_id)
        serializer = RoleSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
