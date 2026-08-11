from django import forms
from .models import Reservation


class ReservationForm(forms.ModelForm):

    class Meta:
        model = Reservation

        exclude = [
            'user',
            'room',
            'check_in_time',
            'check_out_time',
            'status',
            'payment_status',
        ]

