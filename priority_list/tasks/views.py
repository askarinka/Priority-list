from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import Task, WaitingTask


@ensure_csrf_cookie
def index(request):
    tasks = Task.objects.order_by('order', 'id')
    return render(request, 'tasks/index.html', {'tasks': tasks})


def task_add_form(request):
    return render(request, 'tasks/partials/_task_add_row.html')


@require_POST
def task_add(request):
    max_order = Task.objects.aggregate(Max('order'))['order__max'] or 0
    task = Task.objects.create(
        project=request.POST.get('project', '').strip(),
        description=request.POST.get('description', '').strip(),
        order=max_order + 1,
    )
    return render(request, 'tasks/partials/_task_row.html', {'task': task})


def task_row(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/partials/_task_row.html', {'task': task})


def task_edit_form(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/partials/_task_edit_row.html', {'task': task})


@require_POST
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.project = request.POST.get('project', task.project).strip()
    task.description = request.POST.get('description', task.description).strip()
    task.save()
    return render(request, 'tasks/partials/_task_row.html', {'task': task})


@require_POST
def task_delete(request, pk):
    get_object_or_404(Task, pk=pk).delete()
    return HttpResponse('')


@require_POST
def task_reorder(request):
    for i, pk in enumerate(request.POST.getlist('ids')):
        Task.objects.filter(pk=int(pk)).update(order=i)
    return HttpResponse('')


@ensure_csrf_cookie
def waiting_index(request):
    tasks = WaitingTask.objects.order_by('order', 'id')
    return render(request, 'tasks/waiting.html', {'tasks': tasks})


def waiting_add_form(request):
    return render(request, 'tasks/partials/_waiting_add_row.html')


@require_POST
def waiting_add(request):
    max_order = WaitingTask.objects.aggregate(Max('order'))['order__max'] or 0
    task = WaitingTask.objects.create(
        project=request.POST.get('project', '').strip(),
        reason=request.POST.get('reason', '').strip(),
        order=max_order + 1,
    )
    return render(request, 'tasks/partials/_waiting_row.html', {'task': task})


def waiting_row(request, pk):
    task = get_object_or_404(WaitingTask, pk=pk)
    return render(request, 'tasks/partials/_waiting_row.html', {'task': task})


def waiting_edit_form(request, pk):
    task = get_object_or_404(WaitingTask, pk=pk)
    return render(request, 'tasks/partials/_waiting_edit_row.html', {'task': task})


@require_POST
def waiting_edit(request, pk):
    task = get_object_or_404(WaitingTask, pk=pk)
    task.project = request.POST.get('project', task.project).strip()
    task.reason = request.POST.get('reason', task.reason).strip()
    task.save()
    return render(request, 'tasks/partials/_waiting_row.html', {'task': task})


@require_POST
def waiting_delete(request, pk):
    get_object_or_404(WaitingTask, pk=pk).delete()
    return HttpResponse('')


@require_POST
def waiting_reorder(request):
    for i, pk in enumerate(request.POST.getlist('ids')):
        WaitingTask.objects.filter(pk=int(pk)).update(order=i)
    return HttpResponse('')
