from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event

        exclude = ['created_at']

        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'event_time': forms.TimeInput(attrs={'type': 'time'}),
        }