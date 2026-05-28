from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import User
from .forms import (
    RegistrationForm,
    AuthenticationForm,
    ProfileEditForm,
    PasswordChangeForm
)
from projects.models import Project


# ──────────────────────────────────────────────
#  Регистрация
# ──────────────────────────────────────────────
def register(request):
    """Создание нового аккаунта"""
    if request.user.is_authenticated:
        return redirect('projects:list')
    
    form = RegistrationForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        auth_login(request, user)
        messages.success(request, f'Добро пожаловать, {user.name}!')
        return redirect('projects:list')
    
    return render(request, 'users/register.html', {'form': form})


# ──────────────────────────────────────────────
#  Вход / Выход
# ──────────────────────────────────────────────
def login(request):
    """Авторизация пользователя"""
    if request.user.is_authenticated:
        return redirect('projects:list')
    
    form = AuthenticationForm(data=request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        next_url = request.GET.get('next', '/projects/list/')
        return redirect(next_url)
    
    return render(request, 'users/login.html', {'form': form})


def logout(request):
    """Выход из аккаунта"""
    auth_logout(request)
    return redirect('projects:list')


# ──────────────────────────────────────────────
#  Профиль пользователя
# ──────────────────────────────────────────────
def detail(request, user_id):
    """Просмотр профиля пользователя по ID"""
    profile = get_object_or_404(User.objects.select_related(), pk=user_id)
    return render(request, 'users/user-details.html', {
        'user': profile,
    })


@login_required
def edit(request):
    """Редактирование своего профиля"""
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён.')
        return redirect('users:detail', user_id=request.user.pk)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Смена пароля"""
    form = PasswordChangeForm(request.user, request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Пароль изменён.')
        return redirect('users:detail', user_id=request.user.pk)
    
    return render(request, 'users/change_password.html', {'form': form})


# ──────────────────────────────────────────────
#  Список пользователей с фильтрацией
# ──────────────────────────────────────────────
FILTERS = {
    'favorite_authors': 'Авторы избранных проектов',
    'my_project_authors': 'Авторы проектов, в которых я участвую',
    'my_fans': 'Пользователи, которым нравятся мои проекты',
    'my_participants': 'Участники моих проектов',
}


def list_view(request):
    """Список пользователей с возможностью фильтрации"""
    filter_key = request.GET.get('filter', '')
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    
    if request.user.is_authenticated and filter_key in FILTERS:
        queryset = _apply_filter(queryset, filter_key, request.user)
    
    # Пагинация
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/participants.html', {
        'page_obj': page_obj,
        'active_filter': filter_key,
        'query_prefix': f'filter={filter_key}&' if filter_key else '',
    })


def _apply_filter(queryset, filter_key, current_user):
    """Применяет фильтр к queryset пользователей"""
    
    if filter_key == 'favorite_authors':
        # Авторы проектов, которые я добавил в избранное
        fav_projects = current_user.favorites.all()
        author_ids = fav_projects.values_list('owner_id', flat=True)
        return queryset.filter(pk__in=author_ids)
    
    elif filter_key == 'my_project_authors':
        # Авторы проектов, в которых я участвую
        participated = current_user.participated_projects.all()
        author_ids = participated.values_list('owner_id', flat=True)
        return queryset.filter(pk__in=author_ids)
    
    elif filter_key == 'my_fans':
        # Пользователи, которые добавили мои проекты в избранное
        my_projects = Project.objects.filter(owner=current_user)
        fan_ids = User.objects.filter(
            favorites__in=my_projects
        ).values_list('pk', flat=True)
        return queryset.filter(pk__in=fan_ids)
    
    elif filter_key == 'my_participants':
        # Участники моих проектов
        my_projects = Project.objects.filter(owner=current_user)
        participant_ids = User.objects.filter(
            participated_projects__in=my_projects
        ).distinct().values_list('pk', flat=True)
        return queryset.filter(pk__in=participant_ids)
    
    return queryset