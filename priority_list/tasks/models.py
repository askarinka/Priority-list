from django.db import models


class Task(models.Model):
    project = models.CharField(max_length=500)
    description = models.TextField()
    order = models.IntegerField(default=0)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    tracker_url = models.URLField(null=True, blank=True)
    duration_hours = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class WaitingTask(models.Model):
    project = models.CharField(max_length=500)
    reason = models.TextField()
    order = models.IntegerField(default=0)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    tracker_url = models.URLField(null=True, blank=True)
    duration_hours = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
