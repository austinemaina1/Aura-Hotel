from django.db import models
from reservations.models import Reservation

class Invoice(models.Model):

    STATUS_CHOICES = (

        ('Pending', 'Pending'),

        ('Paid', 'Paid'),

    )

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE
    )

    nights = models.IntegerField(
        default=1
    )

    room_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    room_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    extra_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"Invoice #{self.id} - "
            f"{self.reservation.guest_name}"
        )