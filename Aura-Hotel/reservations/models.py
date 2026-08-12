from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room


class Reservation(models.Model):

    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Checked In', 'Checked In'),
        ('Pending Checkout', 'Pending Checkout'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    guest_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )

    check_in = models.DateField()
    check_out = models.DateField()

    check_in_time = models.DateTimeField(
        null=True,
        blank=True
    )

    check_out_time = models.DateTimeField(
        null=True,
        blank=True
    )

    guests = models.IntegerField()

    special_requests = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Booked'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
    auto_now_add=True
    )

    def __str__(self):
        return f"{self.guest_name} - {self.room.room_number}"