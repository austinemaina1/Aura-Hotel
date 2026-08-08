from django.db import models
from django.contrib.auth.models import User



class GuestProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    address = models.CharField(
        max_length=255,
        blank=True
    )

    profile_picture = models.ImageField(
    upload_to='guest_profiles/',
    blank=True,
    null=True
    )

from django import forms
from reviews.models import Review

class GuestReviewForm(forms.ModelForm):

    class Meta:
        model = Review

        fields = [
            'rating',
            'comment'
        ]

    def __str__(self):
        return self.user.username