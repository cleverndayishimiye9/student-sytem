from django.urls import path
from .views import CustomLoginView, logout_view, profile_view, manage_users_view, toggle_user_active

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('users/', manage_users_view, name='manage_users'),
    path('users/<int:user_id>/toggle/', toggle_user_active, name='toggle_user_active'),
]
