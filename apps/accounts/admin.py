from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'phone_number', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('role', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('UoK Profile', {'fields': ('role', 'phone_number', 'profile_photo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('UoK Profile', {'fields': ('role', 'phone_number')}),
    )
