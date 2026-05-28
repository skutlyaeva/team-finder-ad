from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project

ITEMS_PER_PAGE = 12


def _paginate(request, queryset, per_page=ITEMS_PER_PAGE):
    """Возвращает page_obj для переданного queryset."""
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def _get_project_or_json_404(project_id):
    """
    Возвращает (project, None) или (None, JsonResponse с 404).
    Используется в AJAX-вьюхах, где get_object_or_404 недопустим,
    так как возвращает HTML-ответ вместо JSON.
    """
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return None, JsonResponse(
            {'status': 'error', 'message': 'Проект не найден'},
            status=HTTPStatus.NOT_FOUND,
        )
    return project, None


# ──────────────────────────────────────────────
#  Список всех проектов
# ──────────────────────────────────────────────

def list_view(request):
    """Главная страница — все проекты, от новых к старым."""
    qs = Project.objects.select_related('owner').order_by('-created_at')
    return render(request, 'projects/project_list.html', {
        'page_obj': _paginate(request, qs),
        'projects': qs,
    })


# ──────────────────────────────────────────────
#  Детали проекта
# ──────────────────────────────────────────────

def detail(request, project_id):
    """Страница одного проекта."""
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        pk=project_id,
    )
    return render(request, 'projects/project-details.html', {'project': project})


# ──────────────────────────────────────────────
#  Создание проекта
# ──────────────────────────────────────────────

@login_required
def create(request):
    """Форма создания нового проекта."""
    form = ProjectForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        messages.success(request, 'Проект создан!')
        return redirect('projects:detail', project_id=project.pk)

    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False,
    })


# ──────────────────────────────────────────────
#  Редактирование проекта
# ──────────────────────────────────────────────

@login_required
def edit(request, project_id):
    """Форма редактирования проекта (только для автора)."""
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return HttpResponseForbidden('Только автор может редактировать проект')

    form = ProjectForm(request.POST or None, instance=project)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Проект обновлён.')
        return redirect('projects:detail', project_id=project.pk)

    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True,
    })


# ──────────────────────────────────────────────
#  Завершение проекта (AJAX)
# ──────────────────────────────────────────────

@login_required
@require_POST
def complete(request, project_id):
    """Помечает проект как закрытый."""
    project, err = _get_project_or_json_404(project_id)
    if err:
        return err

    if project.owner != request.user:
        return JsonResponse(
            {'status': 'error', 'message': 'Forbidden'},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != Project.Status.OPEN:
        return JsonResponse(
            {'status': 'error', 'message': 'Проект уже закрыт'},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = Project.Status.CLOSED
    project.save()

    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


# ──────────────────────────────────────────────
#  Участие в проекте (AJAX)
# ──────────────────────────────────────────────

@login_required
@require_POST
def toggle_participate(request, project_id):
    """Добавляет или убирает текущего пользователя из участников."""
    project, err = _get_project_or_json_404(project_id)
    if err:
        return err

    user = request.user

    if user == project.owner:
        return JsonResponse(
            {'status': 'error', 'message': 'Автор не может выйти из своего проекта'},
            status=HTTPStatus.BAD_REQUEST,
        )

    is_participant = project.participants.filter(pk=user.pk).exists()

    if is_participant:
        project.participants.remove(user)
    else:
        project.participants.add(user)

    return JsonResponse({'status': 'ok', 'is_participant': not is_participant})


# ──────────────────────────────────────────────
#  Избранное (AJAX)
# ──────────────────────────────────────────────

@login_required
@require_POST
def toggle_favorite(request, project_id):
    """Добавляет или убирает проект из избранного."""
    project, err = _get_project_or_json_404(project_id)
    if err:
        return err

    user = request.user
    is_favorited = user.favorites.filter(pk=project_id).exists()

    if is_favorited:
        user.favorites.remove(project)
    else:
        user.favorites.add(project)

    return JsonResponse({'status': 'ok', 'favorited': not is_favorited})


# ──────────────────────────────────────────────
#  Список избранного
# ──────────────────────────────────────────────

@login_required
def favorites(request):
    """Страница избранных проектов пользователя."""
    qs = request.user.favorites.select_related('owner').order_by('-created_at')
    return render(request, 'projects/favorite_projects.html', {'projects': qs})