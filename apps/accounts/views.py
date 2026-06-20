from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import LoginForm, UserCreationFormCustom, ProfileUpdateForm
from .models import User


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return '/dashboard/'


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def manage_users_view(request):
    """Admin-only: list and create users."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('dashboard')

    users = User.objects.all().order_by('role', 'last_name')
    form = UserCreationFormCustom()

    if request.method == 'POST':
        form = UserCreationFormCustom(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('manage_users')

    return render(request, 'accounts/manage_users.html', {'users': users, 'form': form})


@login_required
def toggle_user_active(request, user_id):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    try:
        user = User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.get_full_name()} has been {status}.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect('manage_users')
