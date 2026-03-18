from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='user_profile'),
    path('profile/delete/', views.delete_account_view, name='delete_account'),
    path('gestion/users/', views.admin_users_view, name='admin_users'),
    path('gestion/users/<int:user_id>/role/', views.admin_change_role_view, name='admin_change_role'),
]
