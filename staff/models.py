from django.db import models

class Staff(models.Model):

    DEPARTMENTS = [
        ('Management', 'Management'),
        ('Reception', 'Reception'),
        ('Restaurant', 'Restaurant'),
        ('Housekeeping', 'Housekeeping'),
        ('Maintenance', 'Maintenance'),
        ('Security', 'Security'),
    ]

    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENTS
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    date_hired = models.DateField()

    def __str__(self):
        return self.full_name
    