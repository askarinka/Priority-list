from django.db import models


class Task(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_BLOCKED_THIS_WEEK = 'blocked_this_week'
    STATUS_BLOCKED_NOT_THIS_WEEK = 'blocked_not_this_week'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_BLOCKED_THIS_WEEK, 'Заблокирована, эта неделя'),
        (STATUS_BLOCKED_NOT_THIS_WEEK, 'Заблокирована, не эта неделя'),
    ]

    project = models.CharField(max_length=500)
    description = models.TextField()
    order = models.IntegerField(default=0)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    tracker_url = models.URLField(null=True, blank=True)
    duration_hours = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    block_reason = models.TextField(blank=True, default='')
    spent_hours = models.IntegerField(default=0)
    spent_minutes = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    @property
    def effective_hours(self):
        if self.status == self.STATUS_BLOCKED_NOT_THIS_WEEK:
            return 0
        total = max(0, self.duration_hours * 60 + self.duration_minutes
                    - self.spent_hours * 60 - self.spent_minutes)
        return total // 60

    @property
    def effective_minutes(self):
        if self.status == self.STATUS_BLOCKED_NOT_THIS_WEEK:
            return 0
        total = max(0, self.duration_hours * 60 + self.duration_minutes
                    - self.spent_hours * 60 - self.spent_minutes)
        return total % 60

