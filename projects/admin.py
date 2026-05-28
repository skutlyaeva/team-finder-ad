from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description', 'owner__email']
    readonly_fields = ['created_at']
    raw_id_fields = ['owner']
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'description', 'github_url')
        }),
        ('Владелец и участники', {
            'fields': ('owner', 'participants')
        }),
        ('Статус', {
            'fields': ('status', 'created_at')
        }),
    )