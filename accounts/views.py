from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q
from .models import User
from .forms import RegisterForm, LoginForm, ProfileForm, RoleForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants incorrects.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès !")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.user.is_admin_user():
        return redirect('admin_dashboard')
    return redirect('user_profile')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('user_profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Compte supprimé.")
        return redirect('login')
    return render(request, 'accounts/delete_account.html')

@login_required
def admin_users_view(request):
    if not request.user.is_admin_user():
        return redirect('user_profile')
    query = request.GET.get('q', '')
    users = User.objects.all().order_by('username')
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    return render(request, 'admin/users.html', {'users': users, 'query': query})

@login_required
def admin_change_role_view(request, user_id):
    if not request.user.is_admin_user():
        return redirect('user_profile')
    target = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, f"Rôle de {target.username} mis à jour.")
            return redirect('admin_users')
    else:
        form = RoleForm(instance=target)
    return render(request, 'admin/change_role.html', {'form': form, 'target': target})
