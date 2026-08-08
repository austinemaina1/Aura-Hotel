from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):

    ACTION_TYPES = (
        ('Reservation', 'Reservation'),
        ('Check In', 'Check In'),
        ('Check Out', 'Check Out'),
        ('Payment', 'Payment'),
        ('Housekeeping', 'Housekeeping'),
        ('Room Status', 'Room Status'),
        ('Staff', 'Staff'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.action_type} - {self.created_at}"