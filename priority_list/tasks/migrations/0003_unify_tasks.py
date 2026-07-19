from django.db import migrations, models
from django.db.models import Max


def migrate_waiting_tasks(apps, schema_editor):
    WaitingTask = apps.get_model('tasks', 'WaitingTask')
    Task = apps.get_model('tasks', 'Task')
    max_order = Task.objects.aggregate(m=Max('order'))['m'] or 0
    for i, wt in enumerate(WaitingTask.objects.order_by('order', 'id')):
        Task.objects.create(
            project=wt.project,
            description='',
            order=max_order + 1 + i,
            external_id=wt.external_id,
            tracker_url=wt.tracker_url,
            duration_hours=wt.duration_hours,
            duration_minutes=wt.duration_minutes,
            status='blocked_not_this_week',
            block_reason=wt.reason,
            spent_hours=0,
            spent_minutes=0,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0002_task_duration_hours_task_duration_minutes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Активна'),
                    ('blocked_this_week', 'Заблокирована, эта неделя'),
                    ('blocked_not_this_week', 'Заблокирована, не эта неделя'),
                ],
                default='active',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='block_reason',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='task',
            name='spent_hours',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='task',
            name='spent_minutes',
            field=models.IntegerField(default=0),
        ),
        migrations.RunPython(migrate_waiting_tasks, migrations.RunPython.noop),
        migrations.DeleteModel('WaitingTask'),
    ]
