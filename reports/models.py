from django.db import models
from django.conf import settings


class ReportLog(models.Model):

    report_name = models.CharField(max_length=200)

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    total_tickets = models.IntegerField(default=0)
    open_tickets = models.IntegerField(default=0)
    closed_tickets = models.IntegerField(default=0)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.report_name