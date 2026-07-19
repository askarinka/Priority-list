from django.test import TestCase, Client
from django.urls import reverse
from .models import Task


class TaskModelTest(TestCase):
    def test_create_task_with_defaults(self):
        task = Task.objects.create(project='Proj', description='Desc', order=0)
        self.assertEqual(Task.objects.count(), 1)
        self.assertIsNone(task.external_id)
        self.assertIsNone(task.tracker_url)

    def test_task_default_duration_is_zero(self):
        task = Task.objects.create(project='P', description='D', order=0)
        self.assertEqual(task.duration_hours, 0)
        self.assertEqual(task.duration_minutes, 0)

    def test_task_default_status_is_active(self):
        task = Task.objects.create(project='P', description='D', order=0)
        self.assertEqual(task.status, 'active')

    def test_effective_hours_active(self):
        task = Task.objects.create(
            project='P', description='D', order=0, status='active',
            duration_hours=5, duration_minutes=30,
            spent_hours=2, spent_minutes=0,
        )
        self.assertEqual(task.effective_hours, 3)
        self.assertEqual(task.effective_minutes, 30)

    def test_effective_hours_blocked_not_this_week_is_zero(self):
        task = Task.objects.create(
            project='P', description='D', order=0,
            status='blocked_not_this_week',
            duration_hours=5, duration_minutes=0,
        )
        self.assertEqual(task.effective_hours, 0)
        self.assertEqual(task.effective_minutes, 0)

    def test_effective_hours_blocked_this_week_counts(self):
        task = Task.objects.create(
            project='P', description='D', order=0,
            status='blocked_this_week',
            duration_hours=3, duration_minutes=0,
            spent_hours=1, spent_minutes=0,
        )
        self.assertEqual(task.effective_hours, 2)
        self.assertEqual(task.effective_minutes, 0)

    def test_effective_hours_clamped_to_zero(self):
        task = Task.objects.create(
            project='P', description='D', order=0, status='active',
            duration_hours=1, duration_minutes=0,
            spent_hours=3, spent_minutes=0,
        )
        self.assertEqual(task.effective_hours, 0)
        self.assertEqual(task.effective_minutes, 0)


class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.task = Task.objects.create(project='P1', description='D1', order=0)

    def test_index_returns_200_with_task(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P1')

    def test_index_filter_active(self):
        Task.objects.create(project='P2', description='D2', order=1,
                            status='blocked_not_this_week')
        response = self.client.get(reverse('index') + '?filter=active')
        self.assertContains(response, 'P1')
        self.assertNotContains(response, 'P2')

    def test_index_filter_blocked(self):
        Task.objects.create(project='P2', description='D2', order=1,
                            status='blocked_not_this_week')
        response = self.client.get(reverse('index') + '?filter=blocked')
        self.assertNotContains(response, 'P1')
        self.assertContains(response, 'P2')

    def test_task_add_form_returns_partial(self):
        response = self.client.get(reverse('task_add_form'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'task-add-row')

    def test_task_row_returns_partial(self):
        response = self.client.get(reverse('task_row', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P1')

    def test_task_edit_form_returns_partial_with_values(self):
        response = self.client.get(reverse('task_edit_form', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P1')

    def test_add_task_creates_and_returns_row(self):
        response = self.client.post(reverse('task_add'), {'project': 'P2', 'description': 'D2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 2)
        self.assertContains(response, 'P2')

    def test_edit_task_updates_and_returns_row(self):
        response = self.client.post(
            reverse('task_edit', args=[self.task.pk]),
            {'project': 'Updated', 'description': 'D1'},
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.project, 'Updated')
        self.assertContains(response, 'Updated')

    def test_delete_task_removes_it(self):
        response = self.client.post(reverse('task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
        self.assertEqual(Task.objects.count(), 0)

    def test_reorder_tasks_updates_order(self):
        t2 = Task.objects.create(project='P2', description='D2', order=1)
        response = self.client.post(
            reverse('task_reorder'),
            {'ids': [t2.pk, self.task.pk]},
        )
        self.assertEqual(response.status_code, 200)
        t2.refresh_from_db()
        self.task.refresh_from_db()
        self.assertEqual(t2.order, 0)
        self.assertEqual(self.task.order, 1)

    def test_add_task_saves_duration(self):
        response = self.client.post(
            reverse('task_add'),
            {'project': 'P2', 'description': 'D2', 'duration_hours': '2', 'duration_minutes': '30'},
        )
        self.assertEqual(response.status_code, 200)
        task = Task.objects.latest('id')
        self.assertEqual(task.duration_hours, 2)
        self.assertEqual(task.duration_minutes, 30)

    def test_edit_task_saves_duration(self):
        response = self.client.post(
            reverse('task_edit', args=[self.task.pk]),
            {'project': 'P1', 'description': 'D1', 'duration_hours': '1', 'duration_minutes': '45'},
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.duration_hours, 1)
        self.assertEqual(self.task.duration_minutes, 45)

    def test_add_task_saves_spent(self):
        response = self.client.post(
            reverse('task_add'),
            {'project': 'P2', 'description': 'D2', 'duration_hours': '3',
             'duration_minutes': '0', 'spent_hours': '1', 'spent_minutes': '30'},
        )
        self.assertEqual(response.status_code, 200)
        task = Task.objects.latest('id')
        self.assertEqual(task.spent_hours, 1)
        self.assertEqual(task.spent_minutes, 30)

    def test_add_task_saves_status_and_block_reason(self):
        response = self.client.post(
            reverse('task_add'),
            {'project': 'P2', 'description': 'D2',
             'status': 'blocked_this_week', 'block_reason': 'Waiting for API'},
        )
        self.assertEqual(response.status_code, 200)
        task = Task.objects.latest('id')
        self.assertEqual(task.status, 'blocked_this_week')
        self.assertEqual(task.block_reason, 'Waiting for API')

    def test_task_row_shows_duration(self):
        task = Task.objects.create(
            project='P', description='D', order=99,
            duration_hours=1, duration_minutes=30,
        )
        response = self.client.get(reverse('task_row', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1ч')
        self.assertContains(response, '30м')
