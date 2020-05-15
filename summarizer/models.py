from django.db import models
from django.utils import timezone

# Create your models here.
class FeedbacksSum(models.Model):
    feedback_ids = models.TextField()
    feedback_all = models.TextField()
    summary = models.TextField()
    insert_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(default=timezone.now)