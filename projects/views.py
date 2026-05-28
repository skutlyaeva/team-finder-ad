from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Project
from .forms import ProjectForm


ITEMS_PER_PAGE = 12


# ──────────────────────────────────────────────
#  Список всех проектов
# ──────────────────────────────────────────────
def list_view(request):
    """Главная страница — все проекты, от новых к старым"""
    qs = Project.objects.select_related('owner').order_by('-created_at')
    paginator = Paginator(qs, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'projects': qs,
    })


# ──────────────────────────────────────────────
#  Детали проекта
# ──────────────────────────────────────────────
def detail(request, project_id):
    """Страница одного проекта"""
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        pk=project_id
    )
    return render(request, 'projects/project-details.html', {
        'project': project,
    })


# ──────────────────────────────────────────────
#  Создание проекта
# ──────────────────────────────────────────────
@login_required
def create(request):
    """Форма создания нового проекта"""
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
    """Форма редактирования проекта (только для автора)"""
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
    """Помечает проект как закрытый"""
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    if project.status != Project.Status.OPEN:
        return JsonResponse({'status': 'error', 'message': 'Проект уже закрыт'}, status=400)

    project.status = Project.Status.CLOSED
    project.save()

    return JsonResponse({
        'status': 'ok',
        'project_status': 'closed'
    })


# ──────────────────────────────────────────────
#  Участие в проекте (AJAX)
# ──────────────────────────────────────────────
@login_required
@require_POST
def toggle_participate(request, project_id):
    """Добавляет или убирает текущего пользователя из участников"""
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if user == project.owner:
        return JsonResponse({
            'status': 'error',
            'message': 'Автор не может выйти из своего проекта'
        }, status=400)

    is_participant = project.participants.filter(pk=user.pk).exists()

    if is_participant:
        project.participants.remove(user)
    else:
        project.participants.add(user)

    return JsonResponse({
        'status': 'ok',
        'is_participant': not is_participant,
    })


# ──────────────────────────────────────────────
#  Избранное (AJAX)
# ──────────────────────────────────────────────
@login_required
@require_POST
def toggle_favorite(request, project_id):
    """Добавляет или убирает проект из избранного"""
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    is_favorited = user.favorites.filter(pk=project_id).exists()

    if is_favorited:
        user.favorites.remove(project)
    else:
        user.favorites.add(project)

    return JsonResponse({
        'status': 'ok',
        'favorited': not is_favorited,
    })


# ──────────────────────────────────────────────
#  Список избранного
# ──────────────────────────────────────────────
@login_required
def favorites(request):
    """Страница избранных проектов пользователя"""
    qs = request.user.favorites.select_related('owner').order_by('-created_at')
    return render(request, 'projects/favorite_projects.html', {
        'projects': qs,
    })