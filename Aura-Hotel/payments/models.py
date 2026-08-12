from django.db import models
from reservations.models import Reservation


class Payment(models.Model):

    PAYMENT_METHODS = (
        ('Mpesa', 'Mpesa'),
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Bank', 'Bank Transfer'),
    )

    STATUS = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    )

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    transaction_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Paid'
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    PAYMENT_CHOICES = [
    ('Pending', 'Pending'),
    ('Paid', 'Paid'),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.reservation.guest_name} - KSh {self.amount}"