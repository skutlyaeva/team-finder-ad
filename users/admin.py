from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ['email', 'name', 'surname', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'name', 'surname']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Учётные данные', {
            'fields': ('email', 'password')
        }),
        ('Профиль', {
            'fields': ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')
        }),
        ('Избранное', {
            'fields': ('favorites',)
        }),
        ('Разрешения', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Даты', {
            'fields': ('date_joined',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined']
    filter_horizontal = ['favorites', 'groups', 'user_permissions']