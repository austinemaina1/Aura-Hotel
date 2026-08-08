from django.db import models

class Contact(models.Model):

    full_name = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=20)

    email = models.EmailField()

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name