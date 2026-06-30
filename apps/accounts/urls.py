from django.urls import path
from .views import (
    CustomLoginView, logout_view, profile_view,
    manage_users_view, toggle_user_active,
    register_student_view, student_list_with_parents
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('users/', manage_users_view, name='manage_users'),
    path('users/<int:user_id>/toggle/', toggle_user_active, name='toggle_user_active'),
    path('register-student/', register_student_view, name='register_student'),
    path('students-parents/', student_list_with_parents, name='student_list_with_parents'),
]