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

    nights = models.IntegerField(default=1)

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

    def update_total(self):

        items_total = sum(
            item.total_price
            for item in self.items.all()
        )

        self.total_amount = (
            self.room_charge +
            self.extra_charges +
            items_total
        )

        self.save(
            update_fields=['total_amount']
        )

    def __str__(self):

        return (
            f"Invoice #{self.id} - "
            f"{self.reservation.guest_name}"
        )


    from django.db import models
from billing.models import Invoice


class InvoiceItem(models.Model):

    CHARGE_TYPES = (
        ('Restaurant', 'Restaurant'),
        ('Laundry', 'Laundry'),
        ('Mini Bar', 'Mini Bar'),
        ('Spa', 'Spa'),
        ('Transport', 'Transport'),
        ('Other', 'Other'),
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )

    description = models.CharField(
        max_length=50,
        choices=CHARGE_TYPES
    )

    quantity = models.IntegerField(
        default=1
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        self.total_price = (
            self.quantity *
            self.unit_price
        )

        super().save(*args, **kwargs)

        self.invoice.update_total()

    def __str__(self):

        return (
            f"{self.description} - "
            f"KSh {self.total_price}"
        )