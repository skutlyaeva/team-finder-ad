from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('list/', views.list_view, name='list'),
    path('edit-profile/', views.edit, name='edit'),
    path('change-password/', views.change_password, name='change_password'),
    path('<int:user_id>/', views.detail, name='detail'),
]