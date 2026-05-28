from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('projects/list/', views.list_view, name='list'),
    path('projects/create-project/', views.create, name='create'),
    path('projects/favorites/', views.favorites, name='favorites'),
    path('projects/<int:project_id>/', views.detail, name='detail'),
    path('projects/<int:project_id>/edit/', views.edit, name='edit'),
    path('projects/<int:project_id>/complete/', views.complete, name='complete'),
    path('projects/<int:project_id>/toggle-participate/', views.toggle_participate, name='toggle_participate'),
    path('projects/<int:project_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]