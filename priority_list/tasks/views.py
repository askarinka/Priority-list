import datetime

from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import Task


@ensure_csrf_cookie
def index(request):
    filter_param = request.GET.get('filter', 'all')
    tasks = Task.objects.order_by('order', 'id')
    if filter_param == 'active':
        tasks = tasks.filter(status='active')
    elif filter_param == 'blocked':
        tasks = tasks.filter(status__in=['blocked_this_week', 'blocked_not_this_week'])
    return render(request, 'tasks/index.html', {'tasks': tasks, 'filter': filter_param})


def task_add_form(request):
    return render(request, 'tasks/partials/_task_add_row.html')


@require_POST
def task_add(request):
    max_order = Task.objects.aggregate(Max('order'))['order__max'] or 0
    task = Task.objects.create(
        project=request.POST.get('project', '').strip(),
        description=request.POST.get('description', '').strip(),
        order=max_order + 1,
        status=request.POST.get('status', 'active'),
        block_reason=request.POST.get('block_reason', '').strip(),
        duration_hours=int(request.POST.get('duration_hours', 0) or 0),
        duration_minutes=int(request.POST.get('duration_minutes', 0) or 0),
        spent_hours=int(request.POST.get('spent_hours', 0) or 0),
        spent_minutes=int(request.POST.get('spent_minutes', 0) or 0),
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
    task.status = request.POST.get('status', task.status)
    task.block_reason = request.POST.get('block_reason', task.block_reason).strip()
    task.duration_hours = int(request.POST.get('duration_hours', task.duration_hours) or 0)
    task.duration_minutes = int(request.POST.get('duration_minutes', task.duration_minutes) or 0)
    task.spent_hours = int(request.POST.get('spent_hours', task.spent_hours) or 0)
    task.spent_minutes = int(request.POST.get('spent_minutes', task.spent_minutes) or 0)
    task.save()
    return render(request, 'tasks/partials/_task_row.html', {'task': task})


@require_POST
def task_delete(request, pk):
    get_object_or_404(Task, pk=pk).delete()
    return HttpResponse('')


@require_POST
def outlook_import(request):
    from django.conf import settings
    import requests as http
    import icalendar

    ics_url = settings.OUTLOOK_ICS_URL
    if not ics_url:
        return HttpResponse('Добавьте OUTLOOK_ICS_URL в .env', status=500)

    try:
        resp = http.get(ics_url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return HttpResponse(f'Ошибка загрузки календаря: {e}', status=500)

    try:
        cal = icalendar.Calendar.from_ical(resp.content)
    except Exception as e:
        return HttpResponse(f'Ошибка разбора ICS: {e}', status=500)

    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)

    max_order = Task.objects.aggregate(Max('order'))['order__max'] or 0
    for component in cal.walk():
        if component.name != 'VEVENT':
            continue
        status = str(component.get('STATUS', '')).upper()
        if status == 'CANCELLED':
            continue
        transp = str(component.get('TRANSP', '')).upper()
        if transp == 'TRANSPARENT':
            continue

        dtstart = component.get('DTSTART')
        dtend = component.get('DTEND')
        if not dtstart or not dtend:
            continue

        start = dtstart.dt
        end = dtend.dt

        # skip all-day events (date, not datetime)
        if not isinstance(start, datetime.datetime):
            continue

        start_date = start.date() if hasattr(start, 'date') else start
        if not (monday <= start_date <= sunday):
            continue

        uid = str(component.get('UID', ''))
        if uid and Task.objects.filter(external_id=uid).exists():
            continue

        total_minutes = max(0, int((end - start).total_seconds() // 60))
        subject = str(component.get('SUMMARY', 'Без названия'))
        max_order += 1
        Task.objects.create(
            project='Встреча',
            description=subject,
            order=max_order,
            external_id=uid or None,
            duration_hours=total_minutes // 60,
            duration_minutes=total_minutes % 60,
            status='active',
        )

    response = HttpResponse('')
    response['HX-Redirect'] = '/'
    return response


@require_POST
def task_reorder(request):
    with transaction.atomic():
        for i, pk in enumerate(request.POST.getlist('ids')):
            Task.objects.filter(pk=int(pk)).update(order=i)
    return HttpResponse('')
