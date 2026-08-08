from django.db import models

class Room(models.Model):

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Cleaning', 'Cleaning'),
        ('Maintenance', 'Maintenance'),
    ]

    room_number = models.CharField(max_length=10)

    room_type = models.CharField(max_length=50)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    def __str__(self):
        return self.room_number