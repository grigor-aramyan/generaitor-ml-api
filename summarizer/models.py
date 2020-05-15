from django.db import models
from django.utils import timezone

# Create your models here.
class FeedbacksSum(models.Model):
    feedback_ids = models.TextField()
    feedback_all = models.TextField()
    summary = models.TextField()
    insert_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(default=timezone.now)


class Feedback(models.Model):
    organization_name = models.CharField(blank=False, max_length=255)
    for_product = models.BooleanField()
    product_id = models.BigIntegerField()
    branch_address = models.TextField()
    sentiment = models.IntegerField()
    keywords = models.CharField(blank=False, max_length=255)
    content = models.TextField()
    feedback_sum = models.ForeignKey(FeedbacksSum, on_delete=models.CASCADE)
    