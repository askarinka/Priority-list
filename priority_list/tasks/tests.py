from django.test import TestCase, Client
from django.urls import reverse
from .models import Task, WaitingTask


class TaskModelTest(TestCase):
    def test_create_task_with_defaults(self):
        task = Task.objects.create(project='Proj', description='Desc', order=0)
        self.assertEqual(Task.objects.count(), 1)
        self.assertIsNone(task.external_id)
        self.assertIsNone(task.tracker_url)

    def test_create_waiting_task_with_defaults(self):
        task = WaitingTask.objects.create(project='Proj', reason='Reason', order=0)
        self.assertEqual(WaitingTask.objects.count(), 1)
        self.assertIsNone(task.external_id)
        self.assertIsNone(task.tracker_url)
