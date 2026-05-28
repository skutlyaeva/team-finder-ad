from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import Project

from .forms import AuthenticationForm, PasswordChangeForm, ProfileEditForm, RegistrationForm
from .models import User

USERS_PER_PAGE = 12

FILTER_FAVORITE_AUTHORS = 'favorite_authors'
FILTER_MY_PROJECT_AUTHORS = 'my_project_authors'
FILTER_MY_FANS = 'my_fans'
FILTER_MY_PARTICIPANTS = 'my_participants'

FILTERS = {
    FILTER_FAVORITE_AUTHORS: 'Авторы избранных проектов',
    FILTER_MY_PROJECT_AUTHORS: 'Авторы проектов, в которых я участвую',
    FILTER_MY_FANS: 'Пользователи, которым нравятся мои проекты',
    FILTER_MY_PARTICIPANTS: 'Участники моих проектов',
}


def _paginate(request, queryset, per_page=USERS_PER_PAGE):
    """Возвращает page_obj для переданного queryset."""
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


# ──────────────────────────────────────────────
#  Регистрация
# ──────────────────────────────────────────────

def register(request):
    """Создание нового аккаунта."""
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
    """Авторизация пользователя."""
    if request.user.is_authenticated:
        return redirect('projects:list')

    form = AuthenticationForm(data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.get_user())
        next_url = request.GET.get('next', '/projects/list/')
        return redirect(next_url)

    return render(request, 'users/login.html', {'form': form})


def logout(request):
    """Выход из аккаунта."""
    auth_logout(request)
    return redirect('projects:list')


# ──────────────────────────────────────────────
#  Профиль пользователя
# ──────────────────────────────────────────────

def detail(request, user_id):
    """Просмотр профиля пользователя по ID."""
    profile = get_object_or_404(User.objects.select_related(), pk=user_id)
    return render(request, 'users/user-details.html', {'user': profile})


@login_required
def edit(request):
    """Редактирование своего профиля."""
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён.')
        return redirect('users:detail', user_id=request.user.pk)

    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Смена пароля."""
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

def list_view(request):
    """Список пользователей с возможностью фильтрации."""
    filter_key = request.GET.get('filter', '')
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')

    if request.user.is_authenticated and filter_key in FILTERS:
        queryset = _apply_filter(queryset, filter_key, request.user)

    return render(request, 'users/participants.html', {
        'page_obj': _paginate(request, queryset),
        'active_filter': filter_key,
        'query_prefix': f'filter={filter_key}&' if filter_key else '',
    })


def _apply_filter(queryset, filter_key, current_user):
    """Применяет фильтр к queryset пользователей."""

    if filter_key == FILTER_FAVORITE_AUTHORS:
        # Авторы проектов, которые я добавил в избранное
        return queryset.filter(
            owned_projects__interested_users=current_user,
        )

    if filter_key == FILTER_MY_PROJECT_AUTHORS:
        # Авторы проектов, в которых я участвую
        return queryset.filter(
            owned_projects__participants=current_user,
        )

    if filter_key == FILTER_MY_FANS:
        # Пользователи, которые добавили мои проекты в избранное
        return queryset.filter(
            favorites__owner=current_user,
        ).distinct()

    if filter_key == FILTER_MY_PARTICIPANTS:
        # Участники моих проектов
        return queryset.filter(
            participated_projects__owner=current_user,
        ).distinct()

    return queryset